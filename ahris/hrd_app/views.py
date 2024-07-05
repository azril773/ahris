# DJANGO
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db import IntegrityError 
from django.db.models import Q, Avg, Max, Min, Sum, Count, F 
from django.http import HttpResponse, JsonResponse
from datetime import date, datetime, timedelta
from django.template.loader import get_template
from django.contrib import messages
from json import dumps
import requests
# SUPPORT
from openpyxl.styles import Alignment, Font
from collections import namedtuple
from openpyxl import Workbook
from xhtml2pdf import pisa
import math
import json
import time
import pandas as pd

# PYZK / FINGER MACHINE
from zk import ZK, const
from struct import pack
from zk import user as us
import codecs  

# MODEL / DATABASE
from .models import *
from django.core.serializers import serialize # Create your views here.

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Functions

def nama_hari(en_day):
    if en_day == "Monday":
        hari = "Senin"
        return hari
    elif en_day == "Tuesday":    
        hari = "Selasa"
        return hari
    elif en_day == "Wednesday":    
        hari = "Rabu"
        return hari
    elif en_day == "Thursday":    
        hari = "Kamis"
        return hari
    elif en_day == "Friday":    
        hari = "Jumat"
        return hari
    elif en_day == "Saturday":    
        hari = "Sabtu"
        return hari
    elif en_day == "Sunday":    
        hari = "Minggu"
        return hari   


def nama_bulan(int_day):
    if int_day == 1:
        bulan = "Januari"
        return bulan
    elif int_day == 2:    
        bulan = "Pebruari"
        return bulan
    elif int_day == 3:    
        bulan = "Maret"
        return bulan
    elif int_day == 4:    
        bulan = "April"
        return bulan
    elif int_day == 5:    
        bulan = "Mei"
        return bulan
    elif int_day == 6:    
        bulan = "Juni"
        return bulan
    elif int_day == 7:    
        bulan = "Juli"
        return bulan
    elif int_day == 8:    
        bulan = "Agustus"
        return bulan
    elif int_day == 9:    
        bulan = "September"
        return bulan
    elif int_day == 10:    
        bulan = "Oktober"
        return bulan
    elif int_day == 11:    
        bulan = "Nopember"
        return bulan
    elif int_day == 12:    
        bulan = "Desember"
        return bulan                                             


def list_bulan():
    data = [
        {'id':1, 'bulan':'Januari'},
        {'id':2, 'bulan':'Pebruari'},
        {'id':3, 'bulan':'Maret'},
        {'id':4, 'bulan':'April'},
        {'id':5, 'bulan':'Mei'},
        {'id':6, 'bulan':'Juni'},
        {'id':7, 'bulan':'Juli'},
        {'id':8, 'bulan':'Agustus'},
        {'id':9, 'bulan':'September'},
        {'id':10, 'bulan':'Oktober'},
        {'id':11, 'bulan':'November'},
        {'id':12, 'bulan':'Desember'},
    ]
    
    return data


class Finger():

    def __init__(self, size, uid, fid, valid, template):
        self.size = len(template) # template only
        self.uid = int(uid)
        self.fid = int(fid)
        self.valid = int(valid)
        self.template = template
        #self.mark = str().encode("hex")
        self.mark = codecs.encode(template[:8], 'hex') + b'...' + codecs.encode(template[-8:], 'hex')

    def repack(self): #full
        return pack("HHbb%is" % (self.size), self.size+6, self.uid, self.fid, self.valid, self.template)

    def repack_only(self): #only template
        return pack("H%is" % (self.size), self.size, self.template)

    
    @staticmethod
    def json_unpack(json):
        return Finger(
            size=json['size'],
            uid=json['uid'],
            fid=json['fid'],
            valid=json['valid'],
            template=codecs.decode(json['template'],'hex')
        )

    def json_pack(self): #packs for json
        return {
            "size": self.size,
            "uid": self.uid,
            "fid": self.fid,
            "valid": self.valid,
            "template": codecs.encode(self.template, 'hex').decode('ascii')
        }


    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return "<Finger> [uid:{:>3}, fid:{}, size:{:>4} v:{} t:{}]".format(self.uid, self.fid, self.size, self.valid, self.mark)

    def __repr__(self):
        return "<Finger> [uid:{:>3}, fid:{}, size:{:>4} v:{} t:{}]".format(self.uid, self.fid, self.size, self.valid, self.mark)

    def dump(self):
        return "<Finger> [uid:{:>3}, fid:{}, size:{:>4} v:{} t:{}]".format(self.uid, self.fid, self.size, self.valid, codecs.encode(self.template, 'hex'))
    
    
def periode_absen(bulan,tahun):
        
    nperiode = '{} {}'.format(nama_bulan(int(bulan)), tahun)
    nbulan = nama_bulan(int(bulan))
    dperiode = int(bulan)
    dtahun = tahun
    
    if bulan == 1:
        tgl1 = '{}-{}-{}'.format(int(tahun)-1, 12, 26)
        tgl2 = '{}-{}-{}'.format(int(tahun), int(bulan), 25)
    else:
        tgl1 = '{}-{}-{}'.format(int(tahun), int(bulan)-1, 26)
        tgl2 = '{}-{}-{}'.format(int(tahun), int(bulan), 25)    
        
    dari_periode = datetime.strptime(tgl1, '%Y-%m-%d')
    sampai_periode = datetime.strptime(tgl2, '%Y-%m-%d')
    prd = dperiode
    thn = dtahun
    
    data = (dari_periode,sampai_periode, prd, thn)
    
    return data       


def periode_skrg():
    
    today = date.today()
        
    tgl_skrg = today.day
    bulan_skrg = today.month
    tahun_skrg = today.year   
    
    if tgl_skrg < 26:    
        nperiode = '{} {}'.format(nama_bulan(int(bulan_skrg)), tahun_skrg)
        nbulan = nama_bulan(int(bulan_skrg))
        dperiode = int(bulan_skrg)
        dtahun = tahun_skrg
        
        if bulan_skrg == 1:        
            tgl1 = '{}-{}-{}'.format(int(tahun_skrg)-1, 12, 26)
            tgl2 = '{}-{}-{}'.format(int(tahun_skrg), int(bulan_skrg), 25) 
        else:    
            tgl1 = '{}-{}-{}'.format(int(tahun_skrg), int(bulan_skrg)-1, 26)
            tgl2 = '{}-{}-{}'.format(int(tahun_skrg), int(bulan_skrg), 25) 
    else:    
        if bulan_skrg == 12:
            nperiode = '{} {}'.format(nama_bulan(1), int(tahun_skrg)+1)
            nbulan = nama_bulan(1)
            dperiode = 1
            dtahun = int(tahun_skrg)+1
            
            tgl1 = '{}-{}-{}'.format(int(tahun_skrg), int(bulan_skrg), 26)
            tgl2 = '{}-{}-{}'.format(int(tahun_skrg)+1, 1, 25)    
        else:    
            nperiode = '{} {}'.format(nama_bulan(int(bulan_skrg)+1), tahun_skrg)
            nbulan = nama_bulan(int(bulan_skrg)+1)
            dperiode = int(bulan_skrg)+1
            dtahun = tahun_skrg
            
            tgl1 = '{}-{}-{}'.format(int(tahun_skrg), int(bulan_skrg), 26)
            tgl2 = '{}-{}-{}'.format(int(tahun_skrg), int(bulan_skrg)+1, 25)         
        
    dari_periode = datetime.strptime(tgl1, '%Y-%m-%d')
    sampai_periode = datetime.strptime(tgl2, '%Y-%m-%d')
    prd = dperiode
    thn = dtahun
    
    data = (dari_periode,sampai_periode, prd, thn)
    
    return data   


def periode_tgl(tanggal):
    
    ftgl = datetime.strptime(tanggal,'%d-%m-%Y')
    
    dtgl = ftgl.day
    dbln = ftgl.month
    dthn = ftgl.year
    
    if dtgl < 26:    
        dperiode = int(dbln)
        dtahun = int(dthn)
        if dperiode == 1:
            dr = '{}-{}-{}'.format(dtahun - 1, 12, 26)
            sp = '{}-{}-{}'.format(dtahun, dperiode, 25)
        else:    
            dr = '{}-{}-{}'.format(dtahun, dperiode - 1, 26)
            sp = '{}-{}-{}'.format(dtahun, dperiode, 25)
    else:    
        if dbln == 12:
            dperiode = 1
            dtahun = int(dthn) + 1
            dr = '{}-{}-{}'.format(dtahun - 1, 12, 26)
            sp = '{}-{}-{}'.format(dtahun, dperiode, 25)
        else:
            dperiode = int(dbln) + 1
            dtahun = int(dthn)             
            dr = '{}-{}-{}'.format(dtahun, dperiode - 1, 26)
            sp = '{}-{}-{}'.format(dtahun, dperiode, 25)
            
    dr=dr
    sp=sp
    prd = dperiode
    thn = dtahun
    
    data = (dr,sp,prd, thn)
    
    return data       


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Dispatch & Login


@login_required
def logindispatch(request):
    request.POST.get('next')


# Logout
def user_logout(request):
    logout(request)
    return redirect("login")
        

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Home

        
@login_required
def beranda(request):  
    
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses        
        dsid = dakses.sid_id
        
        today = date.today()
        
        data = {
            'akses' : akses,
            'today' : today,
            'dsid' : dsid,
        }
        
        return render(request,'hrd_app/beranda.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('noakses')


@login_required
def beranda_no_akses(request):    

    messages.info(request, 'Data akses Anda belum di tentukan.')        
    return redirect('beranda')


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Pegawai


@login_required
def pegawai(request,sid):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.all().order_by('id')       
        # status = serialize("json",status)
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'status' : status,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/pegawai.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def pegawai_non_aktif(request,sid):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.all().order_by('id')       
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'status' : status,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/non_aktif.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def edit_pegawai(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        pg = pegawai_db.objects.get(id=int(idp))
        counter = counter_db.objects.all().order_by('counter')
        divisi = divisi_db.objects.all().order_by('divisi')
        jabatan = jabatan_db.objects.all().order_by('jabatan')
        kk = kelompok_kerja_db.objects.all().order_by('kelompok')
        hr = hari_db.objects.all()
        keluarga = keluarga_db.objects.filter(pegawai_id=int(idp))
        kontak_lain = kontak_lain_db.objects.filter(pegawai_id=int(idp))
        pengalaman = pengalaman_db.objects.filter(pegawai_id=int(idp))
        pendidikan = pendidikan_db.objects.filter(pegawai_id=int(idp))
        pribadi = pribadi_db.objects.get(pegawai_id=pg.pk)
        today = date.today()
        krg = []
        kln = []
        pgl = []
        pdk = []

        for k in keluarga:
            obj = {
                "hubungan":k.hubungan,
                "nama":k.nama,
                "tgl_lahir":k.tgl_lahir.strftime("%Y-%m-%d"),
                "gender":k.gender,
                "gol_darah":k.gol_darah
            }
            krg.append(obj)

        
        for kl in kontak_lain:
            obj = {
                "hubungan":kl.hubungan,
                "nama":kl.nama,
                "gender":kl.gender,
                "phone":kl.phone
            }
            kln.append(obj)
        
        for pd in pendidikan:
            obj = {
                "pendidikan":pd.pendidikan,
                "id":1,
                "nama":pd.nama,
                "kota":pd.kota,
                "dari_tahun":pd.dari_tahun.strftime("%Y-%m-%d"),
                "sampai_tahun":pd.sampai_tahun.strftime("%Y-%m-%d"),
                "jurusan":pd.jurusan,
                "gelar":pd.gelar
            }
            pdk.append(obj)

        for pn in pengalaman:
            obj = {
                "perusahaan":pn.perusahaan,
                "kota":pn.kota,
                "dari_tahun":pn.dari_tahun.strftime("%Y-%m-%d"),
                "sampai_tahun":pn.sampai_tahun.strftime("%Y-%m-%d"),
                "jabatan":pn.jabatan
            }
            pgl.append(obj)
        # rsl = requests.get("https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json")
        # for r in rsl.json():
        #     resultk = requests.get('https://www.emsifa.com/api-wilayah-indonesia/api/regencies/'+r["id"]+'.json')
        #     for rk in resultk.json():
        #         kota_kabupaten_db(nama_kota_kabupaten=rk['name']).save()
        # kota_kabupaten = kota_kabupaten_db.objects.values("nama_kota_kabupaten")
        kota_kabupaten = kota_kabupaten_db.objects.all()
        # for k in kota_kabupaten:
        #     kota_kabupaten_db(nama_kota_kabupaten=k["nama_kota_kabupaten"]).save()
        data = serialize("json",kota_kabupaten)

        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': pg.status_id,
            'counter': counter,
            'divisi': divisi,
            'jabatan': jabatan,
            'kk':kk,
            'hr':hr,
            'pg':pg,
            'today':datetime.strftime(today,'%d-%m-%Y'),
            'keluarga':krg,
            'kontak_lain':kln,
            'pengalaman':pgl,
            'pendidikan':pdk,
            'pribadi':pribadi,
            'idp':int(idp),
            'kota_kabupaten':json.loads(data),
            'modul_aktif' : 'Pegawai',
            'payroll':["Lainnya","HRD","Owner"],
            'goldarah':['O','A','B','AB'],
            'agama':['Islam','Katholik','Kristen','Hindu','Buddha','Konghucu'] 
        }
        print(data["pengalaman"])
        
        return render(request,'hrd_app/pegawai/edit.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')



@login_required
def tpegawai(r):
    iduser = r.user.id

    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id

        counter = counter_db.objects.all().order_by('counter')
        divisi = divisi_db.objects.all().order_by('divisi')
        jabatan = jabatan_db.objects.all().order_by('jabatan')
        kk = kelompok_kerja_db.objects.all().order_by('kelompok')
        hr = hari_db.objects.all()


        
        data = {
            'akses' : akses,
            'dsid': dsid,
            "counter":counter,
            "divisi":divisi,
            "jabatan":jabatan,
            "kk":kk,
            "hr":hr
        }
    return render(r,"hrd_app/pegawai/tambah.html",data)

@login_required
def tambah_pegawai(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        user = akses_db.objects.get(pk=r.user.id)
        sid = user.sid_id
        nama = r.POST.get("nama")
        gender = r.POST.get("gender")
        tgl_masuk = r.POST.get("tgl_masuk")
        nik = r.POST.get("nik")
        userid = r.POST.get("userid")
        div = r.POST.get("div")
        counter = r.POST.get("counter")
        jabatan = r.POST.get("jabatan")
        kk = r.POST.get("kk")
        hr = r.POST.get("hr")
        ca = r.POST.get("ca")
        rek = r.POST.get("rek")
        payroll = r.POST.get("payroll")
        nks = r.POST.get("nks")
        ntk = r.POST.get("ntk")
        pks = r.POST.get("pks")
        ptk = r.POST.get("ptk")


        # Data Pribadi
        alamat = r.POST.get("alamat")
        phone = r.POST.get("phone")
        email = r.POST.get("email")
        kota_lahir = r.POST.get("kota_lahir")
        tgl_lahir = r.POST.get("tgl_lahir")
        tinggi = r.POST.get("tinggi")
        berat = r.POST.get("berat")
        goldarah = r.POST.get("goldarah")
        agama = r.POST.get("agama")


        keluarga = r.POST.get("keluarga")
        pihak = r.POST.get("pihak")
        keluarga = json.loads(keluarga)
        pihak = json.loads(pihak)
        status_pegawai = status_pegawai_db.objects.get(status="Staff")

        if pegawai_db.objects.filter(nama=nama,gender=gender).exists():
            status = "duplikat"
        else:
            pegawai = pegawai_db(
                nama=nama,
                gender=gender,
                userid=userid,
                status=status_pegawai,
                nik=nik,
                divisi_id=div,
                jabatan_id=jabatan,
                no_rekening=rek,
                no_bpjs_ks=nks,
                no_bpjs_tk=ntk,
                payroll_by=payroll,
                ks_premi=pks,
                tk_premi=ptk,
                aktif=1,
                tgl_masuk=datetime.strptime(str(tgl_masuk),'%d-%m-%Y').strftime("%Y-%m-%d"),
                tgl_aktif=datetime.now().strftime('%Y-%m-%d'),
                hari_off_id=hr,
                kelompok_kerja_id=kk,
                sisa_cuti=12,
                counter_id=counter,
                add_by=r.user.username,
                edit_by=r.user.username

                # status
            )            
            pegawai.save()


            # Tambah Pihak Lain
            pgw = pegawai_db.objects.get(userid=userid)
            for p in pihak:
                tkl = kontak_lain_db(
                pegawai_id=int(pgw.pk),
                hubungan = p['hubungan'],
                nama = p['nama'],
                gender = p['gender'],
                phone = p['phone']
                )
                tkl.save()
            

            # Tambah Keluarga
            for k in keluarga:
                tkeluarga = keluarga_db(
                    pegawai_id=int(pgw.pk),
                    hubungan = k['hubungan'],
                    nama = k["nama_keluarga"],
                    tgl_lahir = datetime.strptime(k['tgl_lahir_keluarga'],'%d-%m-%Y'),
                    gender = k['gender'],
                    gol_darah = k['goldarah']
                )
                tkeluarga.save()

            # Tambah Data Pribadi
            pribadi = pribadi_db(
                pegawai_id=int(pgw.pk),
                alamat=alamat,
                phone=phone,
                email=email,
                kota_lahir=kota_lahir,
                tgl_lahir=datetime.strptime(tgl_lahir,"%d-%m-%Y").strftime("%Y-%m-%d"),
                tinggi_badan=tinggi,
                berat_badan=berat,
                gol_darah=goldarah,
                agama=agama
            )
            print(alamat)
            pribadi.save()
            status = "ok"
            print(sid)
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)


@login_required
def tambah_keluarga(r, idp):
    nama_user = r.user.username
    print(r.POST)
    hubungan = r.POST.get('dhubungan_keluarga')
    dnama = r.POST.get('dnama_keluarga')
    tgl_lahir = r.POST.get('dtgl_lahir_keluarga')
    gender = r.POST.get('dgender_keluarga')
    gol_darah = r.POST.get('dgol_darah')
    
    if keluarga_db.objects.filter(hubungan=hubungan, nama=dnama, pegawai_id=int(idp)).exists():
        status = 'duplikat'
    else:
        tkeluarga = keluarga_db(
            pegawai_id=int(idp),
            hubungan = hubungan,
            nama = dnama,
            tgl_lahir = datetime.strptime(tgl_lahir,'%d-%m-%Y'),
            gender = gender,
            gol_darah = gol_darah
        )
        tkeluarga.save()
        
        didl = keluarga_db.objects.filter(pegawai_id=int(idp)).last()
        idl = didl.id
            
        status = 'ok'
        
    return JsonResponse({"status": status, "idl":idl, "hub":hubungan, "dnama":dnama, "tlahir":tgl_lahir, "gender":gender, "goldarah":gol_darah})


@login_required
def tambah_kl(request, idp):
    nama_user = request.user.username
    
    hubungan = request.POST.get('dhubungan_kl')
    dnama = request.POST.get('dnama_kl')
    gender = request.POST.get('dgender_kl')
    phone = request.POST.get('dphone')
    
    if kontak_lain_db.objects.filter(hubungan=hubungan, nama=dnama, pegawai_id=int(idp)).exists():
        status = 'duplikat'
    else:
        tkl = kontak_lain_db(
            pegawai_id=int(idp),
            hubungan = hubungan,
            nama = dnama,
            gender = gender,
            phone = phone
        )
        tkl.save()
        
        didl_kl = kontak_lain_db.objects.filter(pegawai_id=int(idp)).last()
        idl_kl = didl_kl.id
            
        status = 'ok'
        
    return JsonResponse({"status": status, "idl_kl":idl_kl, "hub_kl":hubungan, "dnama_kl":dnama, "gender_kl":gender, "dphone_kl":phone})


@login_required
def general_data(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'nama':pg.nama,
            'gender':pg.gender,
            'nik':pg.nik,
            'userid':pg.userid,
            'divisi':pg.divisi,
            'counter':pg.counter,
            'jabatan':pg.jabatan.jabatan,
            'tgl_masuk':pg.tgl_masuk,
            'off':pg.hari_off.hari,
            'kkerja':pg.kelompok_kerja,
            'shift':pg.shift,
            'rekening':pg.rekening,
            'payroll':pg.payroll_by,
            'nks':pg.no_bpjs_ks,
            'ntk':pg.no_bpjs_tk,
            'pks':pg.ks_premi,
            'ptk':pg.tk_premi,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/general_data.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def data_pribadi(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/data_pribadi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def pendidikan_kerja(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/pendidikan_pkerja.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def promosi_demosi(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/promosi_demosi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def sangsi(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/sangsi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')



@login_required
def aktif_nonaktif(request):
    nama_user = request.user.username
    idp = request.POST.get('idp')
    nama_modul = request.POST.get('nama_modul')
    
    pg = pegawai_db.objects.get(id=int(idp))
    
    if nama_modul == "Non":
        pg.aktif = 0
    else:
        pg.aktif = 1
        
    pg.edit_by = nama_user
    pg.save()        
    
    status = 'ok'    
    
    return JsonResponse({"status": status})


@login_required
def pegawai_json(request, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        if int(sid) == 0:
            for p in pegawai_db.objects.filter(aktif=1):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y')   
                if p.counter:
                    counter = p.counter.counter
                else:
                    counter = None     
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':p.divisi.divisi,
                    'counter':counter,
                    'jabatan':p.jabatan.jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'kkerja':p.kelompok_kerja.kelompok,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id,
                }
                data.append(pg)
        else: 
            for p in pegawai_db.objects.filter(aktif=1, status_id=int(sid)):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y') 
                
                if p.counter:
                    counter = p.counter.counter
                else:
                    counter = None
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':p.divisi.divisi,
                    'counter':counter,
                    'jabatan':p.jabatan.jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'kkerja':p.kelompok_kerja.kelompok,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id,
                }
                data.append(pg)       
                               
        return JsonResponse({"data": data})


@login_required
def non_aktif_json(request, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        if int(sid) == 0:
            for p in pegawai_db.objects.filter(aktif=0):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y')   
                                           
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':p.divisi.divisi,
                    'counter':p.counter,
                    'jabatan':p.jabatan.jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'kkerja':p.kelompok_kerja.kelompok,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id
                }
                data.append(pg)
        else: 
            for p in pegawai_db.objects.filter(aktif=0, status_id=int(sid)):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y') 
                            
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':p.divisi.divisi,
                    'counter':p.counter,
                    'jabatan':p.jabatan.jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'kkerja':p.kelompok_kerja.kelompok,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id
                }
                data.append(pg)       
                               
        return JsonResponse({"data": data})


@login_required
def detail_pegawai_json(request, idp):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
         
        p = pegawai_db.objects.filter(id=int(idp))
                        
        pg = {
            'idp':p.id,
            'nama':p.nama,
            'gender':p.gender,
            'nik':p.nik,
            'userid':p.userid,
            'divisi':p.divisi.divisi,
            'counter':p.counter,
            'jabatan':p.jabatan.jabatan,
            'tgl_masuk':p.tgl_masuk,
            'nbpjs_ks':p.no_bpjs_ks,
            'nbpjs_tk':p.no_bpjs_tk,
            'libur':p.hari_off.hari,
            'libur2':p.hari_off2.hari,
            'ks':p.ks_premi,
            'tk':p.tk_premi,
            'payroll':p.payroll_by,
            'rekening':p.rekening,
            'kkerja':p.kelompok_kerja.kelompok,
            'sisa_cuti':p.sisa_cuti
        }
        data.append(pg)       
                            
        return JsonResponse({"data": data})

    
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Absensi
 
 
@login_required
def absensi(request,sid):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        today = date.today()
        today_datetime = datetime.strptime(f'{today}','%Y-%m-%d')       
        tmin = today_datetime - timedelta(days=1)
        
        dari = datetime.strptime(f'{tmin}','%Y-%m-%d %H:%M:%S').date()
        sampai = today
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        ###
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')
                
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur.id,
            'dari': dari,
            'sampai': sampai,
            'dr' : dr,
            'sp' : sp,
            'modul_aktif' : 'Absensi'
        }
        
        return render(request,'hrd_app/absensi/absensi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_absensi(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        dr = request.POST.get('ctgl1')
        sp = request.POST.get('ctgl2')
        sid = request.POST.get('sid') 
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date() 
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')
        
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            'sid': int(sid),
            'sil': sid_lembur.id,
            'dari': dari,
            'sampai': sampai,
            'dr' : dr,
            'sp' : sp,
            'modul_aktif' : 'Absensi'
        } 
        
        return render(request,'hrd_app/absensi/cabsen.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_absensi_sid(request,dr, sp, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
                
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')
        
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            'sid': int(sid),
            'dari':dari,
            'sampai':sampai,
            'sil': sid_lembur.id,
            'dr':dr,
            'sp':sp,
            'modul_aktif' : 'Absensi'
        } 
        
        return render(request,'hrd_app/absensi/cabsen.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def absensi_json(request, dr, sp, sid):
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        
        if int(sid) == 0:
            for a in absensi_db.objects.select_related('pegawai').filter(tgl_absen__range=(dari,sampai)).order_by('tgl_absen','pegawai__divisi__divisi'):
                            
                sket = " "
                
                ab = absensi_db.objects.get(id=a.id)     
                hari = ab.tgl_absen.strftime("%A")
                hari_ini = nama_hari(hari) 
                
                if ab.pegawai.counter_id is None:
                    bagian = ab.pegawai.divisi.divisi
                else:
                    bagian = f'{ab.pegawai.divisi.divisi} - {ab.pegawai.counter.counter}' 
                    
                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = None    
                    
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{ab.kembali} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:                  
                    kmb = f'{ab.kembali}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{ab.kembali2}'    
                else:
                    kmb = None        
                
                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = None    
                    
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{ab.kembali} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:                  
                    kmb = f'{ab.kembali}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{ab.kembali2}'
                else:
                    kmb = None            
                                        
                if ab.keterangan_absensi is not None:
                    sket += f'{ab.keterangan_absensi}, '                 
                if ab.keterangan_ijin is not None:
                    sket += f'{ab.keterangan_ijin}, '
                    kijin = ''                
                if ab.keterangan_lain is not None:
                    sket += f'{ab.keterangan_lain}, '                    
                if ab.libur_nasional is not None:
                    sket += f'{ab.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          
                                            
                absen = {
                    'id': ab.id,
                    'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    'nama': ab.pegawai.nama,
                    'nik': ab.pegawai.nik,
                    'userid': ab.pegawai.userid,
                    'bagian': bagian,
                    'masuk': ab.masuk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': ab.pulang,
                    'tj': ab.total_jam_kerja,
                    'ket': sket,
                    'sln': sln,
                    'ln': ab.libur_nasional
                }

                data.append(absen)
            
        else:                        
            for a in absensi_db.objects.select_related('pegawai').filter(tgl_absen__range=(dari,sampai), pegawai__status_id=sid).order_by('tgl_absen','pegawai__divisi__divisi'):
                            
                sket = " "
                
                ab = absensi_db.objects.get(id=a.id)     
                hari = ab.tgl_absen.strftime("%A")
                hari_ini = nama_hari(hari) 
                
                if ab.pegawai.counter_id is None:
                    bagian = ab.pegawai.divisi.divisi
                else:
                    bagian = f'{ab.pegawai.divisi.divisi} - {ab.pegawai.counter.counter}' 
                    
                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = None    
                    
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{ab.kembali} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:                  
                    kmb = f'{ab.kembali}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{ab.kembali2}'    
                else:
                    kmb = None        
                
                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = None    
                    
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{ab.kembali} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:                  
                    kmb = f'{ab.kembali}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{ab.kembali2}'
                else:
                    kmb = None            
                                        
                if ab.keterangan_absensi is not None:
                    sket += f'{ab.keterangan_absensi}, '                 
                if ab.keterangan_ijin is not None:
                    sket += f'{ab.keterangan_ijin}, '
                    kijin = ''                
                if ab.keterangan_lain is not None:
                    sket += f'{ab.keterangan_lain}, '                    
                if ab.libur_nasional is not None:
                    sket += f'{ab.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          
                                            
                absen = {
                    'id': ab.id,
                    'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    'nama': ab.pegawai.nama,
                    'nik': ab.pegawai.nik,
                    'userid': ab.pegawai.userid,
                    'bagian': bagian,
                    'masuk': ab.masuk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': ab.pulang,
                    'tj': ab.total_jam_kerja,
                    'ket': sket,
                    'sln': sln,
                    'ln': ab.libur_nasional
                }

                data.append(absen)
            
        return JsonResponse({"data": data })


@login_required
def pabsen(request):    
    
    t1 = request.POST.get('tgl1')
    t2 = request.POST.get('tgl2')
    sid = request.POST.get('sid')
    
    if t1 != "" and t2 != "":     
        dari = datetime.strptime(f'{t1} 00:00:00', "%d-%m-%Y %H:%M:%S")
        sampai = datetime.strptime(f'{t2} 23:59:59', "%d-%m-%Y %H:%M:%S")
        
        dr = datetime.strftime(dari, "%d-%m-%Y")
        sp = datetime.strftime(sampai, "%d-%m-%Y")
    else:
        tminus1 = date.today() - timedelta (days=1)
        
        dari = datetime.strptime(f'{tminus1} 00:00:00', "%Y-%m-%d %H:%M:%S")
        sampai = datetime.strptime(f'{date.today()} 23:59:59', "%Y-%m-%d %H:%M:%S")    
        
        dr = datetime.strftime(dari, "%d-%m-%Y")
        sp = datetime.strftime(sampai, "%d-%m-%Y")
    
    rangetgl = pd.date_range(dari.date(), sampai.date()).tolist()
    
    pegawai = [] 
    luserid = []  
    
    # buat tabel absen
    for p in pegawai_db.objects.filter(aktif=1):
        
        if int(sid) == 0:
            if p.jabatan_id is None:
                jabatan = None
            else:
                jabatan = p.jabatan.jabatan
            
            if p.counter_id is None:
                counter = None
            else:
                counter = p.counter.counter
                
            if p.hari_off2_id is None:
                ho = None
            else:
                ho = p.hari_off2.hari        
            
            data = {
                'idp' : p.id,
                'nama' : p.nama,
                'userid' : p.userid,
                'gender' : p.gender,
                'status' : p.status.status,
                'status_id' : p.status_id,
                'nik' : p.nik,
                'divisi' : p.divisi.divisi,
                'jabatan' : jabatan,                
                'hari_off' : p.hari_off.hari,
                'hari_off2' : ho,
                'kelompok_kerja' : p.kelompok_kerja.kelompok,
                'sisa_cuti' : p.sisa_cuti,
                'shift' : p.shift,
                'counter' : counter
            }
            pegawai.append(data)        
            luserid.append(p.userid)
        else:
            if int(sid) == p.status_id: 
                
                if p.jabatan_id is None:
                    jabatan = None
                else:
                    jabatan = p.jabatan.jabatan
                
                if p.counter_id is None:
                    counter = None
                else:
                    counter = p.counter.counter
                    
                if p.hari_off2_id is None:
                    ho = None
                else:
                    ho = p.hari_off2.hari        
                
                data = {
                    'idp' : p.id,
                    'nama' : p.nama,
                    'userid' : p.userid,
                    'gender' : p.gender,
                    'status' : p.status.status,
                    'status_id' : p.status_id,
                    'nik' : p.nik,
                    'divisi' : p.divisi.divisi,
                    'jabatan' : jabatan,                
                    'hari_off' : p.hari_off.hari,
                    'hari_off2' : ho,
                    'kelompok_kerja' : p.kelompok_kerja.kelompok,
                    'sisa_cuti' : p.sisa_cuti,
                    'shift' : p.shift,
                    'counter' : counter
                }
                pegawai.append(data)        
                luserid.append(p.userid)       
            else:
                pass
        
        for r in rangetgl:
            if absensi_db.objects.filter(tgl_absen=r, pegawai_id=p.id).exists():
                pass
            else:
                tabsen = absensi_db(
                    tgl_absen = r,
                    pegawai_id = p.id
                )
                tabsen.save()
    
    dmesin = []
    
    # ambil data mesin simpan di att dan dmesin array
    for m in mesin_db.objects.filter(status='Aktif'):
        
        ip = m.ipaddress
        
        conn = None
        zk = ZK(ip, port=4370, timeout=65)
        try:
            conn = zk.connect()
            conn.disable_device()

            # Data absensi
            absensi = conn.get_attendance()

            for a in absensi:
                print(a)
                if dari <= a.timestamp <= sampai:   
                    if a.user_id in luserid:              
                        data = {
                            "userid": a.user_id,
                            "jam_absen": a.timestamp,
                            "punch": a.punch,
                            "mesin": m.nama
                        }
                        
                        dmesin.append(data)   
                    else:
                        pass                 

            conn.enable_device()
        except Exception as e:
            print("Process terminate : {}".format(e))
            messages.error(request, "Process terminate : {}".format(e))

        finally:
            if conn:
                conn.disconnect()
    
    # reordering (ascending)
    att = sorted(dmesin, key=lambda i: i['jam_absen'])
    
    ddr = []
        
    # ambil data raw simpan di ddr
    for d in data_raw_db.objects.filter(jam_absen__date__range=(dari.date(),sampai.date()), userid__in=luserid):
        data = {
            "userid": d.userid,
            "jam_absen": d.jam_absen,
            "punch": d.punch,
            "mesin": d.mesin
        }

        ddr.append(data)              
    
    ddt = []
    
    # ambil data trans simpan di ddt
    for d2 in data_trans_db.objects.filter(jam_absen__date__range=(dari.date(),sampai.date()), userid__in=luserid):
        data = {
            "userid": d2.userid,
            "jam_absen": d2.jam_absen,
            "punch": d2.punch,
            "mesin": d2.mesin,
            "ket": d2.keterangan
        }

        ddt.append(data)
        
    dt = []    
    
    # proses data simpan di dt array
    if not att:
        pass
    else:
        for a in att:
            if a['userid'] in luserid:
                
                # simpan data raw jika belum ada di list ddr
                if a not in ddr:                
                    tambah_data_raw = data_raw_db(
                        userid = a['userid'],
                        jam_absen = a['jam_absen'],
                        punch = a['punch'],
                        mesin = a['mesin']             
                    )                
                    tambah_data_raw.save()
                else:
                    pass 
                    
                # Versi Cirebon
                for r in rangetgl:
                
                    tplus = r + timedelta(days=1)
                    
                    if a['jam_absen'].date() == r.date():
                        ab = absensi_db.objects.select_related('pegawai').get(tgl_absen=r.date(), pegawai__userid=a['userid'])
                                            
                        # masuk
                        if a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 0 and int(a['jam_absen'].hour) > 4 and int(a['jam_absen'].hour) < 18:
                            if ab.masuk is None:
                                ab.masuk = a['jam_absen'].time()
                                ab.save()
                                
                                fdtmasuk = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                data_dtmasuk = {
                                    'userid':a['userid'],
                                    'jam_absen':fdtmasuk,
                                    'punch':a['punch'],
                                    'mesin':a['mesin'],
                                    'ket':'Masuk'
                                }
                                if not dt:
                                    dt.append(data_dtmasuk)
                                else:
                                    if data_dtmasuk not in dt:
                                        dt.append(data_dtmasuk)
                                    else:
                                        pass        
                            else:
                                pass
                        
                        # masuk malam
                        elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 0 and int(a['jam_absen'].hour) > 18:      
                            if ab.masuk is None:
                                if ab.pulang is not None:
                                    if int(ab.pulang.hour) > 9:
                                        try:
                                            ab2 = absensi_db.objects.select_related('pegawai').get(tgl_absen=tplus, pegawai__userid=a['userid'])
                                            if ab2.masuk is None:
                                                ab2.masuk = a['jam_absen'].time()
                                                ab2.save()   
                                                
                                                fdtmasuk_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                                data_dtmasuk_m = {
                                                    'userid':a['userid'],
                                                    'jam_absen':fdtmasuk_m,
                                                    'punch':a['punch'],
                                                    'mesin':a['mesin'],
                                                    'ket':'Masuk Malam'
                                                }
                                                if not dt:
                                                    dt.append(data_dtmasuk_m)
                                                else:
                                                    if data_dtmasuk_m not in dt:
                                                        dt.append(data_dtmasuk_m)
                                                    else:
                                                        pass
                                            else:
                                                pass 
                                        except absensi_db.DoesNotExist:
                                            tabsen = absensi_db(
                                                tgl_absen = tplus,
                                                pegawai_id = ab.pegawai_id,
                                                masuk = a['jam_absen'].time() 
                                            )                               
                                            tabsen.save() 
                                            
                                            fdtmasuk_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtmasuk_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtmasuk_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Masuk Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtmasuk_m)
                                            else:
                                                if data_dtmasuk_m not in dt:
                                                    dt.append(data_dtmasuk_m)
                                                else:
                                                    pass   
                                    else:
                                        ab.masuk = a['jam_absen'].time()
                                        ab.save() 
                                        
                                        fdtmasuk_m = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtmasuk_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtmasuk_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Masuk Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtmasuk_m)
                                        else:
                                            if data_dtmasuk_m not in dt:
                                                dt.append(data_dtmasuk_m)
                                            else:
                                                pass 
                                else:
                                    ab.masuk = a['jam_absen'].time()
                                    ab.save() 
                                    
                                    fdtmasuk_m = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtmasuk_m = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtmasuk_m,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Masuk Malam'
                                    }
                                    if not dt:
                                        dt.append(data_dtmasuk_m)
                                    else:
                                        if data_dtmasuk_m not in dt:
                                            dt.append(data_dtmasuk_m)
                                        else:
                                            pass
                                    
                            else:
                                if int(ab.masuk.hour) > 18:
                                    pass
                                else:
                                    try:
                                        ab2 = absensi_db.objects.select_related('pegawai').get(tgl_absen=tplus, pegawai__userid=a['userid'])
                                        if ab2.masuk is not None:
                                            pass
                                        else:
                                            ab2.masuk = a['jam_absen'].time()
                                            ab2.save()
                                            
                                            fdtmasuk_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtmasuk_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtmasuk_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Masuk Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtmasuk_m)
                                            else:
                                                if data_dtmasuk_m not in dt:
                                                    dt.append(data_dtmasuk_m)
                                                else:
                                                    pass
                                                
                                    except absensi_db.DoesNotExist:
                                        tabsen = absensi_db(
                                            tgl_absen = tplus,
                                            pegawai_id = ab.pegawai_id,
                                            masuk = a['jam_absen'].time() 
                                        )                               
                                        tabsen.save()
                                        
                                        fdtmasuk_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                        data_dtmasuk_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtmasuk_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Masuk Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtmasuk_m)
                                        else:
                                            if data_dtmasuk_m not in dt:
                                                dt.append(data_dtmasuk_m)
                                            else:
                                                pass
                                
                        # istirahat
                        elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 2 and int(a['jam_absen'].hour) > 8 and int(a['jam_absen'].hour) < 21:
                            if ab.masuk is not None:
                                if int(ab.masuk.hour) < 18:
                                    ab.istirahat = a['jam_absen'].time()
                                    ab.save()
                                    
                                    fdtist = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtist = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtist,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Istirahat'
                                    }
                                    if not dt:
                                        dt.append(data_dtist)
                                    else:
                                        if data_dtist not in dt:
                                            dt.append(data_dtist)
                                        else:
                                            pass
                                else:
                                    pass
                            else:
                                if ab.pulang is not None:
                                    if int(ab.pulang.hour) > 9:
                                        ab.istirahat = a['jam_absen'].time()
                                        ab.save() 
                                        
                                        fdtist = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtist = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtist,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Istirahat'
                                        }
                                        if not dt:
                                            dt.append(data_dtist)
                                        else:
                                            if data_dtist not in dt:
                                                dt.append(data_dtist)
                                            else:
                                                pass
                                    else:
                                        pass    
                                else:
                                    ab.istirahat = a['jam_absen'].time()
                                    ab.save()  
                                    
                                    fdtist = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtist = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtist,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Istirahat'
                                    }
                                    if not dt:
                                        dt.append(data_dtist)
                                    else:
                                        if data_dtist not in dt:
                                            dt.append(data_dtist)
                                        else:
                                            pass                 
                        
                        # istirahat malam
                        elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 2 and int(a['jam_absen'].hour) > 21:
                            if ab.masuk is not None:
                                if int(ab.masuk.hour) > 18:
                                    ab.istirahat = a['jam_absen'].time()
                                    ab.save()
                                    
                                    fdtist_m = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtist_m = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtist_m,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Istirahat Malam'
                                    }
                                    if not dt:
                                        dt.append(data_dtist_m)
                                    else:
                                        if data_dtist_m not in dt:
                                            dt.append(data_dtist_m)
                                        else:
                                            pass
                                else:
                                    pass
                            else:
                                if ab.pulang is not None:
                                    if int(ab.pulang.hour) < 9:
                                        ab.istirahat = a['jam_absen'].time()
                                        ab.save() 
                                        
                                        fdtist_m = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtist_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtist_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Istirahat Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtist_m)
                                        else:
                                            if data_dtist_m not in dt:
                                                dt.append(data_dtist_m)
                                            else:
                                                pass
                                    else:
                                        pass    
                                else:
                                    ab.istirahat = a['jam_absen'].time()
                                    ab.save()   
                                    
                                    fdtist_m = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtist_m = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtist_m,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Istirahat Malam'
                                    }
                                    if not dt:
                                        dt.append(data_dtist_m)
                                    else:
                                        if data_dtist_m not in dt:
                                            dt.append(data_dtist_m)
                                        else:
                                            pass                
                                
                        # istirahat 2
                        elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 4 and int(a['jam_absen'].hour) > 8 and int(a['jam_absen'].hour) < 21:
                            if ab.masuk is not None:
                                if int(ab.masuk.hour) < 18:
                                    ab.istirahat2 = a['jam_absen'].time()
                                    ab.save()
                                    
                                    fdtist_2 = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtist_2 = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtist_2,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Istirahat_2'
                                    }
                                    if not dt:
                                        dt.append(data_dtist_2)
                                    else:
                                        if data_dtist_2 not in dt:
                                            dt.append(data_dtist_2)
                                        else:
                                            pass
                                else:
                                    pass
                            else:
                                if ab.pulang is not None:
                                    if int(ab.pulang.hour) > 9:
                                        ab.istirahat2 = a['jam_absen'].time()
                                        ab.save() 
                                        
                                        fdtist_2 = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtist_2 = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtist_2,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Istirahat_2'
                                        }
                                        if not dt:
                                            dt.append(data_dtist_2)
                                        else:
                                            if data_dtist_2 not in dt:
                                                dt.append(data_dtist_2)
                                            else:
                                                pass
                                    else:
                                        pass    
                                else:
                                    ab.istirahat2 = a['jam_absen'].time()
                                    ab.save()   
                                    
                                    fdtist_2 = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtist_2 = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtist_2,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Istirahat_2'
                                    }
                                    if not dt:
                                        dt.append(data_dtist_2)
                                    else:
                                        if data_dtist_2 not in dt:
                                            dt.append(data_dtist_2)
                                        else:
                                            pass           
                            
                        # kembali
                        elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 3 and int(a['jam_absen'].hour) > 8 and int(a['jam_absen'].hour) < 21:
                            if ab.masuk is not None:
                                if int(ab.masuk.hour) < 18:
                                    if ab.kembali is None:
                                        ab.kembali = a['jam_absen'].time()
                                        ab.save()
                                        
                                        fdtkmb = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtkmb = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtkmb,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Kembali Istirahat'
                                        }
                                        if not dt:
                                            dt.append(data_dtkmb)
                                        else:
                                            if data_dtkmb not in dt:
                                                dt.append(data_dtkmb)
                                            else:
                                                pass
                                    else:
                                        pass    
                                else:
                                    pass
                            else:
                                if ab.pulang is not None:
                                    if int(ab.pulang.hour) > 9:
                                        if ab.kembali is None:
                                            ab.kembali = a['jam_absen'].time()
                                            ab.save()
                                            
                                            fdtkmb = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                            data_dtkmb = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtkmb,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Kembali Istirahat'
                                            }
                                            if not dt:
                                                dt.append(data_dtkmb)
                                            else:
                                                if data_dtkmb not in dt:
                                                    dt.append(data_dtkmb)
                                                else:
                                                    pass
                                        else:
                                            pass     
                                    else:
                                        pass    
                                else:
                                    if ab.kembali is None:
                                        ab.kembali = a['jam_absen'].time()
                                        ab.save()  
                                        
                                        fdtkmb = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtkmb = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtkmb,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Kembali Istirahat'
                                        }
                                        if not dt:
                                            dt.append(data_dtkmb)
                                        else:
                                            if data_dtkmb not in dt:
                                                dt.append(data_dtkmb)
                                            else:
                                                pass
                                    else:
                                        pass    
                        
                        # kembali malam
                        elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 3 and int(a['jam_absen'].hour) > 21:
                            if ab.masuk is not None:
                                if int(ab.masuk.hour) > 18:
                                    if ab.kembali is None:
                                        ab.kembali = a['jam_absen'].time()
                                        ab.save()
                                        
                                        fdtkmb_m = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtkmb_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtkmb_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Kembali Istirahat Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtkmb_m)
                                        else:
                                            if data_dtkmb_m not in dt:
                                                dt.append(data_dtkmb_m)
                                            else:
                                                pass
                                    else:
                                        pass    
                                else:
                                    pass
                            else:
                                if ab.pulang is not None:
                                    if int(ab.pulang.hour) < 9:
                                        if ab.kembali is None:
                                            ab.kembali = a['jam_absen'].time()
                                            ab.save()
                                            
                                            fdtkmb_m = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                            data_dtkmb_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtkmb_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Kembali Istirahat Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtkmb_m)
                                            else:
                                                if data_dtkmb_m not in dt:
                                                    dt.append(data_dtkmb_m)
                                                else:
                                                    pass
                                        else:
                                            pass     
                                    else:
                                        pass    
                                else:
                                    if ab.kembali is None:
                                        ab.kembali = a['jam_absen'].time()
                                        ab.save()  
                                        
                                        fdtkmb_m = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtkmb_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtkmb_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Kembali Istirahat Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtkmb_m)
                                        else:
                                            if data_dtkmb_m not in dt:
                                                dt.append(data_dtkmb_m)
                                            else:
                                                pass
                                    else:
                                        pass    
                                                    
                        # kembali 2
                        elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 5 and int(a['jam_absen'].hour) > 8 and int(a['jam_absen'].hour) < 21:
                            if ab.masuk is not None:
                                if int(ab.masuk.hour) < 18:
                                    if ab.kembali2 is None:
                                        ab.kembali2 = a['jam_absen'].time()
                                        ab.save()
                                        
                                        fdtkmb_2 = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtkmb_2 = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtkmb_2,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Kembali Istirahat_2'
                                        }
                                        if not dt:
                                            dt.append(data_dtkmb_2)
                                        else:
                                            if data_dtkmb_2 not in dt:
                                                dt.append(data_dtkmb_2)
                                            else:
                                                pass
                                    else:
                                        pass    
                                else:
                                    pass
                            else:
                                if ab.pulang is not None:
                                    if int(ab.pulang.hour) > 9:
                                        if ab.kembali2 is None:
                                            ab.kembali2 = a['jam_absen'].time()
                                            ab.save()
                                            
                                            fdtkmb_2 = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                            data_dtkmb_2 = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtkmb_2,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Kembali Istirahat_2'
                                            }
                                            if not dt:
                                                dt.append(data_dtkmb_2)
                                            else:
                                                if data_dtkmb_2 not in dt:
                                                    dt.append(data_dtkmb_2)
                                                else:
                                                    pass
                                        else:
                                            pass     
                                    else:
                                        pass    
                                else:
                                    if ab.kembali2 is None:
                                        ab.kembali2 = a['jam_absen'].time()
                                        ab.save()  
                                        
                                        fdtkmb_2 = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtkmb_2 = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtkmb_2,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Kembali Istirahat_2'
                                        }
                                        if not dt:
                                            dt.append(data_dtkmb_2)
                                        else:
                                            if data_dtkmb_2 not in dt:
                                                dt.append(data_dtkmb_2)
                                            else:
                                                pass
                                    else:
                                        pass  
                            
                        # pulang
                        elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == ab.tgl_absen and a['punch'] == 1 and int(a['jam_absen'].hour) > 8:
                            if ab.masuk is not None:
                                if int(ab.masuk.hour) < 18:
                                    ab.pulang = a['jam_absen'].time()
                                    ab.save()
                                    
                                    fdtplng = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtplng = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtplng,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Pulang'
                                    }
                                    if not dt:
                                        dt.append(data_dtplng)
                                    else:
                                        if data_dtplng not in dt:
                                            dt.append(data_dtplng)
                                        else:
                                            pass
                                else:
                                    pass
                            else:
                                if ab.pulang is not None:
                                    if int(ab.pulang.hour) > 9:
                                        ab.pulang = a['jam_absen'].time()
                                        ab.save() 
                                        
                                        fdtplng = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                        data_dtplng = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtplng,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Pulang'
                                        }
                                        if not dt:
                                            dt.append(data_dtplng)
                                        else:
                                            if data_dtplng not in dt:
                                                dt.append(data_dtplng)
                                            else:
                                                pass
                                    else:
                                        pass    
                                else:
                                    ab.pulang = a['jam_absen'].time()
                                    ab.save()  
                                    
                                    fdtplng = f"{ab.tgl_absen} {a['jam_absen'].time()}"
                                    data_dtplng = {
                                        'userid':a['userid'],
                                        'jam_absen':fdtplng,
                                        'punch':a['punch'],
                                        'mesin':a['mesin'],
                                        'ket':'Pulang'
                                    }
                                    if not dt:
                                        dt.append(data_dtplng)
                                    else:
                                        if data_dtplng not in dt:
                                            dt.append(data_dtplng)
                                        else:
                                            pass
                                                
                    else:
                        ab = absensi_db.objects.select_related('pegawai').get(tgl_absen=r.date(), pegawai__userid=a['userid'])               
                        
                        tplus = r + timedelta(days=1)
                        
                        if a['jam_absen'].date() == tplus:
                            
                            # istirahat malam
                            if a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == tplus and a['punch'] == 2 and int(a['jam_absen'].hour) < 9:
                                if ab.masuk is not None:
                                    if int(ab.masuk.hour) > 18:
                                        ab.istirahat = a['jam_absen'].time()
                                        ab.save()
                                        
                                        fdtist_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                        data_dtist_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtist_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Istirahat Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtist_m)
                                        else:
                                            if data_dtist_m not in dt:
                                                dt.append(data_dtist_m)
                                            else:
                                                pass
                                    else:
                                        pass
                                else:
                                    if ab.pulang is not None:
                                        if int(ab.pulang.hour) < 9:
                                            ab.istirahat = a['jam_absen'].time()
                                            ab.save()
                                            
                                            fdtist_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtist_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtist_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Istirahat Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtist_m)
                                            else:
                                                if data_dtist_m not in dt:
                                                    dt.append(data_dtist_m)
                                                else:
                                                    pass
                                        else:
                                            pass
                                    else:
                                        ab.istirahat = a['jam_absen'].time()
                                        ab.save()   
                                        
                                        fdtist_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                        data_dtist_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtist_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Istirahat Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtist_m)
                                        else:
                                            if data_dtist_m not in dt:
                                                dt.append(data_dtist_m)
                                            else:
                                                pass
                            
                            # kembali malam
                            elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == tplus and a['punch'] == 3 and int(a['jam_absen'].hour) < 9:                            
                                if ab.masuk is None:
                                    if ab.pulang is None:
                                        ab.kembali = a['jam_absen'].time()
                                        ab.save()
                                        
                                        fdtkmb_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                        data_dtkmb_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtkmb_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Kembali Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtkmb_m)
                                        else:
                                            if data_dtkmb_m not in dt:
                                                dt.append(data_dtkmb_m)
                                            else:
                                                pass
                                    else:
                                        if int(ab.pulang.hour) < 9:
                                            ab.kembali = a['jam_absen'].time()
                                            ab.save()
                                            
                                            fdtkmb_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtkmb_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtkmb_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Kembali Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtkmb_m)
                                            else:
                                                if data_dtkmb_m not in dt:
                                                    dt.append(data_dtkmb_m)
                                                else:
                                                    pass
                                        else:
                                            if int(ab.pulang.hour) > 9:
                                                try:
                                                    ab2 = absensi_db.objects.select_related('pegawai').get(tgl_absen=tplus, pegawai__userid=a['userid'])
                                                    ab2.kembali = a['jam_absen'].time()
                                                    ab2.save()
                                                    
                                                    fdtkmb_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                                    data_dtkmb_m = {
                                                        'userid':a['userid'],
                                                        'jam_absen':fdtkmb_m,
                                                        'punch':a['punch'],
                                                        'mesin':a['mesin'],
                                                        'ket':'Kembali Malam'
                                                    }
                                                    if not dt:
                                                        dt.append(data_dtkmb_m)
                                                    else:
                                                        if data_dtkmb_m not in dt:
                                                            dt.append(data_dtkmb_m)
                                                        else:
                                                            pass
                                                        
                                                except absensi_db.DoesNotExist:
                                                    tabsen = absensi_db(
                                                        tgl_absen = tplus,
                                                        pegawai_id = ab.pegawai_id,
                                                        kembali = a['jam_absen'].time() 
                                                    )                               
                                                    tabsen.save()
                                                    
                                                    fdtkmb_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                                    data_dtkmb_m = {
                                                        'userid':a['userid'],
                                                        'jam_absen':fdtkmb_m,
                                                        'punch':a['punch'],
                                                        'mesin':a['mesin'],
                                                        'ket':'Kembali Malam'
                                                    }
                                                    if not dt:
                                                        dt.append(data_dtkmb_m)
                                                    else:
                                                        if data_dtkmb_m not in dt:
                                                            dt.append(data_dtkmb_m)
                                                        else:
                                                            pass
                                else:
                                    if int(ab.masuk.hour) > 18:
                                        ab.kembali = a['jam_absen'].time()
                                        ab.save() 
                                        
                                        fdtkmb_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                        data_dtkmb_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtkmb_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Kembali Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtkmb_m)
                                        else:
                                            if data_dtkmb_m not in dt:
                                                dt.append(data_dtkmb_m)
                                            else:
                                                pass         
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.select_related('pegawai').get(tgl_absen=tplus, pegawai__userid=a['userid'])
                                            ab2.kembali = a['jam_absen'].time()
                                            ab2.save()
                                            
                                            fdtkmb_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtkmb_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtkmb_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Kembali Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtkmb_m)
                                            else:
                                                if data_dtkmb_m not in dt:
                                                    dt.append(data_dtkmb_m)
                                                else:
                                                    pass
                                                
                                        except absensi_db.DoesNotExist:
                                            tabsen = absensi_db(
                                                tgl_absen = tplus,
                                                pegawai_id = ab.pegawai_id,
                                                kembali = a['jam_absen'].time() 
                                            )                               
                                            tabsen.save()
                                            
                                            fdtkmb_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtkmb_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtkmb_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Kembali Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtkmb_m)
                                            else:
                                                if data_dtkmb_m not in dt:
                                                    dt.append(data_dtkmb_m)
                                                else:
                                                    pass
                    
                            # pulang malam
                            elif a['userid'] == ab.pegawai.userid and a['jam_absen'].date() == tplus and a['punch'] == 1 and int(a['jam_absen'].hour) < 9:
                                
                                if ab.masuk is None:
                                    if ab.pulang is None:
                                        ab.pulang = a['jam_absen'].time()
                                        ab.save()
                                        
                                        fdtplng_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                        data_dtplng_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtplng_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Pulang Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtplng_m)
                                        else:
                                            if data_dtplng_m not in dt:
                                                dt.append(data_dtplng_m)
                                            else:
                                                pass
                                    else:
                                        if int(ab.pulang.hour) < 9:
                                            ab.pulang = a['jam_absen'].time()
                                            ab.save()
                                            
                                            fdtplng_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtplng_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtplng_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Pulang Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtplng_m)
                                            else:
                                                if data_dtplng_m not in dt:
                                                    dt.append(data_dtplng_m)
                                                else:
                                                    pass
                                        else:
                                            if int(ab.pulang.hour) > 9:
                                                try:
                                                    ab2 = absensi_db.objects.select_related('pegawai').get(tgl_absen=tplus, pegawai__userid=a['userid'])
                                                    ab2.pulang = a['jam_absen'].time()
                                                    ab2.save()
                                                    
                                                    fdtplng_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                                    data_dtplng_m = {
                                                        'userid':a['userid'],
                                                        'jam_absen':fdtplng_m,
                                                        'punch':a['punch'],
                                                        'mesin':a['mesin'],
                                                        'ket':'Pulang Malam'
                                                    }
                                                    if not dt:
                                                        dt.append(data_dtplng_m)
                                                    else:
                                                        if data_dtplng_m not in dt:
                                                            dt.append(data_dtplng_m)
                                                        else:
                                                            pass
                                                        
                                                except absensi_db.DoesNotExist:
                                                    tabsen = absensi_db(
                                                        tgl_absen = tplus,
                                                        pegawai_id = ab.pegawai_id,
                                                        pulang = a['jam_absen'].time() 
                                                    )                               
                                                    tabsen.save()
                                                    
                                                    fdtplng_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                                    data_dtplng_m = {
                                                        'userid':a['userid'],
                                                        'jam_absen':fdtplng_m,
                                                        'punch':a['punch'],
                                                        'mesin':a['mesin'],
                                                        'ket':'Pulang Malam'
                                                    }
                                                    if not dt:
                                                        dt.append(data_dtplng_m)
                                                    else:
                                                        if data_dtplng_m not in dt:
                                                            dt.append(data_dtplng_m)
                                                        else:
                                                            pass
                                else:
                                    if int(ab.masuk.hour) > 18:
                                        ab.pulang = a['jam_absen'].time()
                                        ab.save()   
                                        
                                        fdtplng_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                        data_dtplng_m = {
                                            'userid':a['userid'],
                                            'jam_absen':fdtplng_m,
                                            'punch':a['punch'],
                                            'mesin':a['mesin'],
                                            'ket':'Pulang Malam'
                                        }
                                        if not dt:
                                            dt.append(data_dtplng_m)
                                        else:
                                            if data_dtplng_m not in dt:
                                                dt.append(data_dtplng_m)
                                            else:
                                                pass       
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.select_related('pegawai').get(tgl_absen=tplus, pegawai__userid=a['userid'])
                                            ab2.pulang = a['jam_absen'].time()
                                            ab2.save()
                                            
                                            fdtplng_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtplng_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtplng_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Pulang Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtplng_m)
                                            else:
                                                if data_dtplng_m not in dt:
                                                    dt.append(data_dtplng_m)
                                                else:
                                                    pass
                                                
                                        except absensi_db.DoesNotExist:
                                            tabsen = absensi_db(
                                                tgl_absen = tplus,
                                                pegawai_id = ab.pegawai_id,
                                                pulang = a['jam_absen'].time() 
                                            )                               
                                            tabsen.save()
                                            
                                            fdtplng_m = f"{tplus.date()} {a['jam_absen'].time()}"
                                            data_dtplng_m = {
                                                'userid':a['userid'],
                                                'jam_absen':fdtplng_m,
                                                'punch':a['punch'],
                                                'mesin':a['mesin'],
                                                'ket':'Pulang Malam'
                                            }
                                            if not dt:
                                                dt.append(data_dtplng_m)
                                            else:
                                                if data_dtplng_m not in dt:
                                                    dt.append(data_dtplng_m)
                                                else:
                                                    pass
            
                        else:
                            pass      
                      
            else:
                pass                
            
    # simpan data trans
    for b in dt:
        if b not in ddt:                
            tambah_data_trans = data_trans_db(
                userid = b['userid'],
                jam_absen = b['jam_absen'],
                punch = b['punch'],
                mesin = b['mesin'],
                keterangan = b['ket']             
            )                
            tambah_data_trans.save()
        else:
            pass 
    
    ijin = []  
    libur = []
    cuti = []
    geser = []
    opg = []
    dl = []
    dl_idp = []
    
    lsopg = []
    
    # list status pegawai yang dapat opg
    for s in list_status_opg_db.objects.all():
        lsopg.append(s.status_id)
    
    # data ijin
    for i in ijin_db.objects.select_related('ijin','pegawai').filter(tgl_ijin__range=(dari.date(),sampai.date())):
        data = {
            "ijin" : i.ijin.ijin,
            "tgl_ijin" : i.tgl_ijin,
            "idp" : i.pegawai_id,
            "keterangan" : i.keterangan
        }
        ijin.append(data)
    
    # data libur nasional
    for l in libur_nasional_db.objects.filter(tgl_libur__range=(dari.date(),sampai.date())):
        data = {
            'libur' : l.libur,
            'tgl_libur' : l.tgl_libur,
            'insentif_karyawan' : l.insentif_karyawan,
            'insentif_staff' : l.insentif_staff
        }    
        libur.append(data)  
        
    # data cuti
    for c in cuti_db.objects.select_related('pegawai').filter(tgl_cuti__range=(dari.date(),sampai.date())):
        data = {
            'id': c.id,
            'idp' : c.pegawai_id,
            'tgl_cuti' : c.tgl_cuti,
            'keterangan' : c.keterangan
        }                
        cuti.append(data)
        
    # data geser off
    for g in geseroff_db.objects.select_related('pegawai').filter(ke_tgl__range=(dari.date(),sampai.date())):
        data = {
            'id' : g.id,
            'idp' : g.pegawai_id, 
            'dari_tgl' : g.dari_tgl,
            'ke_tgl' : g.ke_tgl,
            'keterangan' : g.keterangan
        } 
        geser.append(data)
        
    # data opg
    for o in opg_db.objects.select_related('pegawai').filter(diambil_tgl__range=(dari.date(),sampai.date()), status=0):
        data = {
            'id':o.id,
            'idp': o.pegawai_id,
            'opg_tgl':o.opg_tgl,
            'diambil_tgl':o.diambil_tgl,
            'keterangan':o.keterangan
        }
        opg.append(data)
    
    # data dinas luar
    for n in dinas_luar_db.objects.select_related('pegawai').filter(tgl_dinas__range=(dari.date(),sampai.date())):
        data = {
            'idp': n.pegawai_id,
            'tgl_dinas':n.tgl_dinas,
            'keterangan':n.keterangan
        }
        dl.append(data)
        dl_idp.append(n.pegawai_id)
        
    # data absensi
    for a in absensi_db.objects.select_related('pegawai').filter(tgl_absen__range=(dari.date(),sampai.date())):
        
        day = a.tgl_absen.strftime("%A")
        nh = nama_hari(day)        
        
        for p in pegawai:
            if a.pegawai_id == p['idp']:
                ab = absensi_db.objects.select_related('pegawai').get(id=a.id)               
                
                """ Rules OPG (staff & karyawan) & Insentif (hanya untuk karyawan) :
                
                Staff :
                --> jika ada libur nasional dan jatuh di hari biasa (senin - sabtu), maka staff yang memiliki off reguler bertepatan
                dengan libur nasional tersebut akan mendapat opg = 2 jika masuk (off pengganti reguler dan off pengganti tgl merah), 
                jika tidak masuk mendapat opg = 1 (off pengganti reguler)
                
                --> jika ada libur nasional dan jatuh di hari minggu, maka staff yang memiliki off reguler bertepatan dengan libur
                nasional tersebut jika masuk mendapat opg = 1 (off pengganti reguler)
                
                --> jika tidak ada libur nasional, maka staff yang masuk di hari off regulernya maka mendapat opg = 1 (off pengganti 
                reguler)
                
                Karyawan + SPG dibayar oleh Asia:
                --> jika ada libur nasional (senin - minggu), maka Karyawan yang memiliki off reguler bertepatan
                dengan libur nasional tersebut akan mendapat opg = 1 jika masuk (off pengganti reguler) dan insentif = 1
                                
                --> jika tidak ada libur nasional, maka Karyawan yang masuk di hari off regulernya maka mendapat opg = 1 (off pengganti 
                reguler)
                
                """     
                
                # OFF & OFF Pengganti Reguler
                # jika tidak ada absen masuk dan pulang
                if ab.masuk is None and ab.pulang is None:
                                        
                    # jika dinas luar
                    if ab.pegawai_id in dl_idp:
                        
                        # jika off
                        if p['hari_off'] == nh:
                            if p['status_id'] in lsopg:
                                if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                    pass
                                else:
                                    if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                        pass
                                    else:
                                        tambah_opg = opg_db(
                                            pegawai_id = ab.pegawai_id,
                                            opg_tgl = ab.tgl_absen,   
                                            keterangan = 'OFF Pengganti Reguler',                         
                                            add_by = 'Program',
                                        )    
                                        tambah_opg.save()
                            else:
                                pass
                        else:
                            if p['hari_off'] == 'On Off':
                                ab.keterangan_absensi = 'OFF'
                                ab.save()
                            else:
                                pass
                            
                        if p['hari_off2'] == nh:
                            if p['status_id'] in lsopg:
                                if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                    pass
                                else:
                                    if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                        pass
                                    else:
                                        tambah_opg = opg_db(
                                            pegawai_id = ab.pegawai_id,
                                            opg_tgl = ab.tgl_absen,   
                                            keterangan = 'OFF Pengganti Reguler',                         
                                            add_by = 'Program',
                                        )    
                                        tambah_opg.save()
                            else:
                                pass
                        else:
                            pass    
                    else:
                        # jika off
                        if p['hari_off'] == nh:
                            ab.keterangan_absensi = 'OFF'
                            ab.save()
                        elif p['hari_off'] == 'On Off':
                            ab.keterangan_absensi = 'OFF'
                            ab.save()    
                                    
                        if p['hari_off2'] == nh:
                            ab.keterangan_absensi = 'OFF'
                            ab.save() 
                        else:
                            pass           
                                            
                else:
                    # jika off
                    if p['hari_off'] == nh:
                        if p['status_id'] in lsopg:
                            if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                pass
                            else:
                                if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                    pass
                                else:
                                    tambah_opg = opg_db(
                                        pegawai_id = ab.pegawai_id,
                                        opg_tgl = ab.tgl_absen,   
                                        keterangan = 'OFF Pengganti Reguler',                         
                                        add_by = 'Program',
                                    )    
                                    tambah_opg.save()
                        else:
                            pass
                    else:
                        pass
                    
                    if p['hari_off2'] == nh:
                        if p['status_id'] in lsopg:
                            if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                pass
                            else:
                                if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                    pass
                                else:
                                    tambah_opg = opg_db(
                                        pegawai_id = ab.pegawai_id,
                                        opg_tgl = ab.tgl_absen,   
                                        keterangan = 'OFF Pengganti Reguler',                         
                                        add_by = 'Program',
                                    )    
                                    tambah_opg.save()
                        else:
                            pass
                    else:
                        pass
                            
                # libur nasional
                for l in libur:
                    if l['tgl_libur'] == ab.tgl_absen:                            
                        ab.libur_nasional = l['libur']
                        ab.save()
                        
                        # Hari Minggu
                        if nh == 'Minggu':
                            if p['status_id'] in lsopg:
                                
                                # Staff
                                if p['status'] == 'Staff':
                                    if p['hari_off'] == nh:
                                        if ab.masuk is not None and ab.pulang is not None:
                                            if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                                pass
                                            else:
                                                if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                                    pass
                                                else:
                                                    tambah_opg = opg_db(
                                                        pegawai_id = ab.pegawai_id,
                                                        opg_tgl = ab.tgl_absen,   
                                                        keterangan = 'OFF Pengganti Reguler',                         
                                                        add_by = 'Program',
                                                    )    
                                                    tambah_opg.save()
                                        else:
                                            pass    
                                    else:
                                        pass
                                
                                # Karyawan
                                else:
                                    if p['hari_off'] == nh:
                                        if ab.masuk is not None and ab.pulang is not None:
                                            if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                                pass
                                            else:
                                                if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                                    pass
                                                else:
                                                    tambah_opg = opg_db(
                                                        pegawai_id = ab.pegawai_id,
                                                        opg_tgl = ab.tgl_absen,   
                                                        keterangan = 'OFF Pengganti Reguler',                         
                                                        add_by = 'Program',
                                                    )    
                                                    tambah_opg.save()
                                                    
                                                    ab.insentif = l['insentif_karyawan']
                                                    ab.save()
                                        else:
                                            pass    
                                    else:
                                        pass                                
                            else:
                                pass 
                        
                        # Bukan Hari Minggu
                        else:
                            if p['status_id'] in lsopg:
                                                                
                                # Staff
                                if p['status'] == 'Staff':
                                    if p['hari_off'] == nh:
                                        if ab.masuk is not None and ab.pulang is not None:
                                            if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                                pass
                                            else:
                                                if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                                    pass
                                                else:
                                                    tambah_opg = opg_db(
                                                        pegawai_id = ab.pegawai_id,
                                                        opg_tgl = ab.tgl_absen,   
                                                        keterangan = 'OFF Pengganti Reguler',                         
                                                        add_by = 'Program',
                                                    )    
                                                    tambah_opg.save()
                                                    
                                                if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Tgl Merah').exists():
                                                    pass
                                                else:    
                                                    tambah_opg2 = opg_db(
                                                        pegawai_id = ab.pegawai_id,
                                                        opg_tgl = ab.tgl_absen,   
                                                        keterangan = 'OFF Pengganti Tgl Merah',                         
                                                        add_by = 'Program',
                                                    )    
                                                    tambah_opg2.save()
                                        else:
                                            if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Tgl Merah').exists():
                                                pass
                                            else:    
                                                tambah_opg2 = opg_db(
                                                    pegawai_id = ab.pegawai_id,
                                                    opg_tgl = ab.tgl_absen,   
                                                    keterangan = 'OFF Pengganti Tgl Merah',                         
                                                    add_by = 'Program',
                                                )    
                                                tambah_opg2.save()    
                                    else:
                                        pass
                                
                                # Karyawan
                                else:
                                    if p['hari_off'] == nh:
                                        if ab.masuk is not None and ab.pulang is not None:
                                            if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                                pass
                                            else:
                                                if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                                    pass
                                                else:
                                                    tambah_opg = opg_db(
                                                        pegawai_id = ab.pegawai_id,
                                                        opg_tgl = ab.tgl_absen,   
                                                        keterangan = 'OFF Pengganti Reguler',                         
                                                        add_by = 'Program',
                                                    )    
                                                    tambah_opg.save()
                                                    
                                                    ab.insentif = l['insentif_karyawan']
                                                    ab.save()
                                        else:
                                            pass    
                                    else:
                                        pass                                
                            else:
                                pass                                                                    
                    else:
                        pass    
                            
                # ijin
                for i in ijin:
                    if a.pegawai_id == i['idp']:
                        if i['tgl_ijin'] == ab.tgl_absen:
                            ij = i['ijin']
                            ket = i['keterangan']
                            ab.keterangan_ijin = f'{ij}-({ket})'
                            ab.save()
                        else:
                            pass
                    else:
                        pass                                 
                
                # cuti
                for c in cuti:
                    if a.pegawai_id == c['idp']:
                        if c['tgl_cuti'] == ab.tgl_absen:
                            if ab.masuk is None and ab.pulang is None:
                                ab.keterangan_absensi = c['keterangan']
                                ab.save()
                            else:
                                dmsk = f'{ab.tgl_absen} {ab.masuk}'
                                dplg = f'{ab.tgl_absen} {ab.pulang}'
                                
                                msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                
                                dselisih = plg - msk
                                djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S') 
                                
                                if int(selisih.hour) <= 4:
                                    ab.keterangan_absensi = c['keterangan']
                                    ab.save()
                                else:
                                    cuti_db.objects.get(id=int(c['id'])).delete()
                                    pg = pegawai_db.objects.get(pegawai_id=ab.pegawai_id)
                                    sc = pg.sisa_cuti
                                    
                                    pg.sisa_cuti = sc + 1
                                    pg.save()          
                        else:
                            pass
                    else:
                        pass        
                    
                # geser off
                for g in geser:
                    if a.pegawai_id == g['idp']:
                        if g['ke_tgl'] == ab.tgl_absen:
                            if ab.masuk is None and ab.pulang is None:
                                drt = datetime.strftime(g['dari_tgl'], '%d-%m-%Y')
                                ab.keterangan_absensi = f'Geser OFF-({drt})' 
                                ab.save()
                            else:
                                geseroff_db.objects.get(id=int(g['id'])).delete()    
                        else:
                            pass
                
                # opg
                for o in opg:
                    if a.pegawai_id == o['idp']:
                        if o['diambil_tgl'] == ab.tgl_absen:
                            
                            opg = opg_db.objects.get(id=o['id'])
                            
                            if ab.masuk is None and ab.pulang is None:
                                topg = datetime.strftime(o['diambil_tgl'], '%d-%m-%Y')
                                ab.keterangan_absensi = f'OPG-({topg})'
                                ab.save()                                
                                
                                opg.status = 1
                                opg.edit_by ='Program'
                                opg.save()
                            else:
                                opg.diambil_tgl = None
                                opg.edit_by = 'Program'
                                opg.save()
                                    
                        else:
                            pass
                    else:
                        pass        
                
                # dinas luar   
                for n in dl:
                    if a.pegawai_id == n['idp']:
                        if n['tgl_dinas'] == ab.tgl_absen:
                            ket = n['keterangan']
                            ab.keterangan_absensi = f'Dinas Luar-({ket})'
                            ab.save()
                        else:
                            pass    
                    else:
                        pass    
                                        
                # total jam kerja         
                if ab.masuk is not None and ab.pulang is not None:
                    if ab.pulang > ab.masuk:
                        
                        dmsk = f'{ab.tgl_absen} {ab.masuk}'
                        dplg = f'{ab.tgl_absen} {ab.pulang}'
                        
                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih = plg - msk
                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                        selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
                        
                        if int(selisih.hour) <= 4:
                            tjk = 0
                        else:
                            detik = selisih.second / 3600
                            menit = selisih.minute / 60
                            hour = selisih.hour
                            
                            jam = int(hour) + float(menit) + float(detik)
                            
                            tjk = jam                   
                    else: 
                        
                        tplus = ab.tgl_absen + timedelta(days=1)             
                        
                        dmsk = f'{ab.tgl_absen} {ab.masuk}'
                        dplg = f'{tplus} {ab.pulang}'
                        
                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih = plg - msk
                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                        selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
                        
                        if int(selisih.hour) <= 4:
                            tjk = 0
                        else:
                            detik = selisih.second / 3600
                            menit = selisih.minute / 60
                            hour = selisih.hour
                            
                            jam = int(hour) + float(menit) + float(detik)
                            
                            tjk = jam                
                else:
                    tjk = 0
                    
                # total jam istirahat
                if ab.istirahat is not None and ab.kembali is not None:
                    if ab.kembali > ab.istirahat:
                        
                        dist = f'{ab.tgl_absen} {ab.istirahat}'
                        dkmb = f'{ab.tgl_absen} {ab.kembali}'
                        
                        ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
                        kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_i = kmb - ist
                        djam_selisih_i = f'{ab.tgl_absen} {dselisih_i}'
                        selisih_i = datetime.strptime(djam_selisih_i, '%Y-%m-%d %H:%M:%S')
                            
                        detik_i = selisih_i.second / 3600
                        menit_i = selisih_i.minute / 60
                        hour_i = selisih_i.hour
                        
                        jam_i = int(hour_i) + float(menit_i) + float(detik_i)
                        
                        tji = jam_i                   
                    else:
                        
                        tplus = ab.tgl_absen + timedelta(days=1)
                        
                        dist = f'{ab.tgl_absen} {ab.istirahat}'
                        dkmb = f'{tplus} {ab.kembali}'
                        
                        ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
                        kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_i = kmb - ist
                        djam_selisih_i = f'{ab.tgl_absen} {dselisih_i}'
                        selisih_i = datetime.strptime(djam_selisih_i, '%Y-%m-%d %H:%M:%S')
                            
                        detik_i = selisih_i.second / 3600
                        menit_i = selisih_i.minute / 60
                        hour_i = selisih_i.hour
                        
                        jam_i = int(hour_i) + float(menit_i) + float(detik_i)
                        
                        tji = jam_i                      
                else:
                    tji = 0        
                
                # total jam istirahat2
                if ab.istirahat2 is not None and ab.kembali2 is not None:
                    if ab.kembali2 > ab.istirahat2:
                        
                        dist2 = f'{ab.tgl_absen} {ab.istirahat2}'
                        dkmb2 = f'{ab.tgl_absen} {ab.kembali2}'
                        
                        ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
                        kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_i2 = kmb2 - ist2
                        djam_selisih_i2 = f'{ab.tgl_absen} {dselisih_i2}'
                        selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                            
                        detik_i2 = selisih_i2.second / 3600
                        menit_i2 = selisih_i2.minute / 60
                        hour_i2 = selisih_i2.hour
                        
                        jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
                        
                        tji2 = jam_i2                   
                    else:
                        
                        tplus = ab.tgl_absen + timedelta(days=1)
                        
                        dist2 = f'{ab.tgl_absen} {ab.istirahat2}'
                        dkmb2 = f'{tplus} {ab.kembali2}'
                        
                        ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
                        kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_i2 = kmb2 - ist2
                        djam_selisih_i2 = f'{ab.tgl_absen} {dselisih_i2}'
                        selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                            
                        detik_i2 = selisih_i2.second / 3600
                        menit_i2 = selisih_i2.minute / 60
                        hour_i2 = selisih_i2.hour
                        
                        jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
                        
                        tji2 = jam_i2
                else:
                    tji2 = 0    
                    
                ab.total_jam_kerja = tjk
                ab.total_jam_istirahat = tji
                ab.total_jam_istirahat2 = tji2
                ab.save()
                    
            else:
                pass            
                
    return redirect ('cabsen_s',dr=dr, sp=sp, sid=int(sid))   


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ijin


@login_required
def ijin(request, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
        dari = pa[0].date()
        sampai = pa[1].date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
        
        ijin = jenis_ijin_db.objects.order_by('jenis_ijin')
                        
        data = {
            'akses' : akses,
            'today' : today,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : sid,
            'sil': sid_lembur.id,
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(request,'hrd_app/Ijins/ijin/ijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_ijin(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dr = request.POST.get('ctgl1')
        sp = request.POST.get('ctgl2')
        sid = request.POST.get('sid')
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date() 
                
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else: 
                if p.status_id == int(sid):
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)   

        ijin = jenis_ijin_db.objects.order_by('jenis_ijin')
                        
        data = {
            'akses' : akses,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(request,'hrd_app/Ijins/ijin/cijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_ijin_sid(request, dr, sp, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
                
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else: 
                if p.status_id == int(sid):
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)   

        ijin = jenis_ijin_db.objects.order_by('jenis_ijin')
                        
        data = {
            'akses' : akses,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(request,'hrd_app/Ijins/ijin/cijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def ijin_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        
        if int(sid) == 0:
            for i in ijin_db.objects.select_related('pegawai','ijin').filter(tgl_ijin__range=(dari,sampai)):
                
                tijin = i.tgl_ijin.strftime("%A")
                hari = nama_hari(tijin) 
                
                ijin = {
                    'id':i.id,
                    'tgl':datetime.strftime(i.tgl_ijin, '%d-%m-%Y'),
                    'hari':hari,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ijin_id':i.ijin_id,
                    'ijin':i.ijin.jenis_ijin,
                    'ket':i.keterangan
                }
                data.append(ijin)
        else:
            for i in ijin_db.objects.select_related('pegawai','ijin').filter(tgl_ijin__range=(dari,sampai), pegawai__status_id=int(sid)):
                
                tijin = i.tgl_ijin.strftime("%A")
                hari = nama_hari(tijin) 
                
                ijin = {
                    'id':i.id,
                    'tgl':datetime.strftime(i.tgl_ijin, '%d-%m-%Y'),
                    'hari':hari,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ijin_id':i.ijin_id,
                    'ijin':i.ijin.jenis_ijin,
                    'ket':i.keterangan
                }
                data.append(ijin)
            
                                
        return JsonResponse({"data": data})


@login_required
def tambah_ijin(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl')
    dpegawai = request.POST.get('pegawai')
    dijin = request.POST.get('ijin')
    dket = request.POST.get('ket')
    
    ij = jenis_ijin_db.objects.get(id=int(dijin))
        
    ltgl = dtgl.split(', ')
    
    for t in ltgl:
        tgl = datetime.strptime(t,'%d-%m-%Y')        
              
        if ijin_db.objects.select_related('pegawai','ijin').filter(pegawai_id=int(dpegawai), tgl_ijin=tgl.date()).exists():
            status = 'duplikat'
        else:
            if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=tgl.date()).exists():
                ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=tgl.date())
                ab.keterangan_ijin = f'{ij.jenis_ijin}-({dket})'
                ab.save()
            else:
                pass 
                
            tambah = ijin_db(
                ijin_id = int(dijin),
                tgl_ijin = tgl.date(),
                pegawai_id = int(dpegawai),
                keterangan = dket,        
                add_by = nama_user,
                edit_by = nama_user
            )
            tambah.save()

            status = 'ok'    
    
    return JsonResponse({"status": status})


@login_required
def batal_ijin(request):
    nama_user = request.user.username

    id_ijin = request.POST.get('id')
    
    ij = ijin_db.objects.select_related('pegawai','ijin').get(id=int(id_ijin))
    tgl = ij.tgl_ijin
    idp = ij.pegawai_id
    nama_pegawai = ij.pegawai.nama
    jenis_ijin = ij.ijin.jenis_ijin
    
    ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=tgl)
    ab.keterangan_ijin = None
    ab.save()
    
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"{jenis_ijin}-(a.n {nama_pegawai}, tgl:{tgl})"
    )
    histori.save()
    
    ij.delete()
    
    status = 'ok'    
    
    return JsonResponse({"status": status})


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Geser Off

@login_required
def geser_off(request, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
        dari = pa[0].date()
        sampai = pa[1].date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            'today' : today,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/Ijins/geser_off/geser_off.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_geser_off(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dr = request.POST.get('ctgl1')
        sp = request.POST.get('ctgl2')
        sid = request.POST.get('sid')
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/Ijins/geser_off/cgeser_off.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_geser_off_sid(request, dr, sp, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/Ijins/geser_off/cgeser_off.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def geseroff_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
                
        if int(sid) == 0:
            for i in geseroff_db.objects.filter(dari_tgl__range=(dari,sampai)):
                            
                gf = {
                    'id':i.id,
                    'dari_tgl':datetime.strftime(i.dari_tgl, '%d-%m-%Y'),
                    'ke_tgl':datetime.strftime(i.ke_tgl, '%d-%m-%Y'),
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan
                }
                data.append(gf)
        else:
            for i in geseroff_db.objects.select_related('pegawai').filter(dari_tgl__range=(dari,sampai), pegawai__status_id=int(sid)):
                            
                gf = {
                    'id':i.id,
                    'dari_tgl':datetime.strftime(i.dari_tgl, '%d-%m-%Y'),
                    'ke_tgl':datetime.strftime(i.ke_tgl, '%d-%m-%Y'),
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan
                }
                data.append(gf)
                               
        return JsonResponse({"data": data})


@login_required
def tambah_geseroff(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl')
    dtgl2 = request.POST.get('tgl2')
    dpegawai = request.POST.get('pegawai')
    dket = request.POST.get('ket')
    
    dari = datetime.strptime(dtgl,'%d-%m-%Y').date()
    ke = datetime.strptime(dtgl2,'%d-%m-%Y').date()   
    
    fdari = datetime.strftime(dari,'%d-%m-%Y')  
    
    pg = pegawai_db.objects.get(id=int(dpegawai))  
    off = pg.hari_off.hari
    
    if libur_nasional_db.objects.filter(tgl_libur=dari).exists():
        ln = libur_nasional_db.objects.get(tgl_libur=dari)
        tln = ln.tgl_libur
    else:
        tln = None    
    
    day = dari.strftime("%A")
    nh = nama_hari(day) 
            
    if geseroff_db.objects.select_related('pegawai').filter(Q(dari_tgl=dari)|Q(ke_tgl=ke),pegawai_id=int(dpegawai)).exists():
        status = 'duplikat'
    else:        
        
        # cek jika sudah terdapat opg, batalkan
        if opg_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), opg_tgl=dari).exists():
            status = 'ada opg'
        else:
            # cek jika absen di tanggal dari tgl tidak ada absen masuk atau absen pulangnya, batalkan
            if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=dari).exists():
                ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=dari)
                
                if ab.masuk is not None or ab.pulang is not None:
                    
                    # cek jika absen di tanggal ke tgl ada absen masuk atau absen pulangnya, batalakan
                    if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=ke).exists():
                        ab2 = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=ke)
                        
                        if ab2.masuk is not None and ab.pulang is not None:
                            status = 'pegawai masuk'
                        else:
                            if off == nh:
                                tambahgf = geseroff_db(
                                    pegawai_id = int(dpegawai),
                                    dari_tgl = dari,
                                    ke_tgl = ke,
                                    keterangan = dket,
                                    add_by = nama_user,
                                    edit_by = nama_user
                                )
                                tambahgf.save()
                                
                                ab2.keterangan_absensi = f"Geser OFF-({fdari})"
                                ab2.save()
                                
                                status = 'ok'
                            else:
                                if tln is not None:
                                    if dari == tln:
                                        tambahgf = geseroff_db(
                                            pegawai_id = int(dpegawai),
                                            dari_tgl = dari,
                                            ke_tgl = ke,
                                            keterangan = dket,
                                            add_by = nama_user,
                                            edit_by = nama_user
                                        )
                                        tambahgf.save()
                                        
                                        ab2.keterangan_absensi = f"Geser OFF-({fdari})"
                                        ab2.save()
                                        
                                        status = 'ok'
                                    else:
                                        status = 'bukan tgl merah'    
                                else:
                                    status = 'bukan hari off'
                    else:
                        if off == nh:
                            tambahgf = geseroff_db(
                                pegawai_id = int(dpegawai),
                                dari_tgl = dari,
                                ke_tgl = ke,
                                keterangan = dket,
                                add_by = nama_user,
                                edit_by = nama_user
                            )
                            tambahgf.save()
                            
                            status = 'ok'
                        else:
                            if tln is not None:
                                if dari == tln:
                                    tambahgf = geseroff_db(
                                        pegawai_id = int(dpegawai),
                                        dari_tgl = dari,
                                        ke_tgl = ke,
                                        keterangan = dket,
                                        add_by = nama_user,
                                        edit_by = nama_user
                                    )
                                    tambahgf.save()
                                    
                                    status = 'ok'
                                else:
                                    status = 'bukan tgl merah'
                            else:
                                status = 'bukan hari off'   
                    
                else:
                    status = 'pegawai tidak masuk'  

            else:
                if off == nh:
                    tambahgf = geseroff_db(
                        pegawai_id = int(dpegawai),
                        dari_tgl = dari,
                        ke_tgl = ke,
                        keterangan = dket,
                        add_by = nama_user,
                        edit_by = nama_user
                    )
                    tambahgf.save()
                    
                    status = 'ok'
                else:
                    if tln is not None:
                        if dari == tln:
                            tambahgf = geseroff_db(
                                pegawai_id = int(dpegawai),
                                dari_tgl = dari,
                                ke_tgl = ke,
                                keterangan = dket,
                                add_by = nama_user,
                                edit_by = nama_user
                            )
                            tambahgf.save()
                            
                            status = 'ok'
                        else:
                            status = 'bukan tgl merah'
                    else:
                        status = 'bukan hari off'    
    
                    
    return JsonResponse({"status": status})


@login_required
def batal_geseroff(request):
    nama_user = request.user.username

    id_batal = request.POST.get('id_batal')
    
    gf = geseroff_db.objects.select_related('pegawai').get(id=int(id_batal))
    
    ke_tgl = gf.ke_tgl
    dari_tgl = gf.dari_tgl
    idp = gf.pegawai_id
    nama_pegawai = gf.pegawai.nama
        
    if libur_nasional_db.objects.filter(tgl_libur=dari_tgl).exists():
        ln = libur_nasional_db.objects.get(tgl_libur=dari_tgl)
        tln = ln.tgl_libur
        kopg = 'OFF Pengganti Tgl Merah'
    else:
        tln = None 
        kopg = 'OFF Pengganti Reguler'
    
    ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=ke_tgl)
    ab.keterangan_absensi = None
    ab.save()
    
    if opg_db.objects.filter(pegawai_id=int(idp), opg_tgl=dari_tgl).exists():
        pass
    else:
        tambah_opg = opg_db(
            pegawai_id = int(idp),
            opg_tgl = dari_tgl,  
            keterangan = kopg,          
            add_by = 'Program',
            edit_by = 'Program'
        )
        tambah_opg.save()
       
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"Geser OFF-(a.n {nama_pegawai}, tgl:{dari_tgl})"
    )
    histori.save()
    
    gf.delete()    
    
    status = 'ok'    
    
    return JsonResponse({"status": status})


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# OPG

@login_required
def opg(request, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
        dari = pa[0].date()
        sampai = pa[1].date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            'today' : today,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'OPG'
        }
        
        return render(request,'hrd_app/Ijins/opg/opg.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_opg(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dr = request.POST.get('ctgl1')
        sp = request.POST.get('ctgl2')
        sid = request.POST.get('sid')
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'OPG'
        }
        
        return render(request,'hrd_app/Ijins/opg/copg.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_opg_sid(request, dr, sp, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'OPG'
        }
        
        return render(request,'hrd_app/Ijins/opg/copg.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def opg_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
                
        if int(sid) == 0:
            for i in opg_db.objects.filter(opg_tgl__range=(dari,sampai)):
                
                if i.diambil_tgl is not None:
                    dtgl = datetime.strftime(i.diambil_tgl, '%d-%m-%Y')
                else:
                    dtgl = None    
                            
                op = {
                    'id':i.id,
                    'opg_tgl':datetime.strftime(i.opg_tgl, '%d-%m-%Y'),
                    'diambil_tgl':dtgl,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan,
                    'status':i.status
                }
                data.append(op)
        else:
            for i in opg_db.objects.filter(opg_tgl__range=(dari,sampai), pegawai__status_id=int(sid)):
                
                if i.diambil_tgl is not None:
                    dtgl = datetime.strftime(i.diambil_tgl, '%d-%m-%Y')
                else:
                    dtgl = None 
                            
                op = {
                    'id':i.id,
                    'opg_tgl':datetime.strftime(i.opg_tgl, '%d-%m-%Y'),
                    'diambil_tgl':dtgl,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan,
                    'status':i.status
                }
                data.append(op)
                               
        return JsonResponse({"data": data})


@login_required
def tambah_opg(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl')
    dpegawai = request.POST.get('pegawai')
    
    tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()   
    
    pg = pegawai_db.objects.get(id=int(dpegawai))  
    off = pg.hari_off.hari
    
    if libur_nasional_db.objects.filter(tgl_libur=tgl).exists():
        ln = libur_nasional_db.objects.get(tgl_libur=tgl)
        tln = ln.tgl_libur
    else:
        tln = None    
    
    day = tgl.strftime("%A")
    nh = nama_hari(day) 
            
    if opg_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), opg_tgl=tgl).exists():
        status = 'duplikat'
    else:        
        
        # cek jika sudah terdapat opg, batalkan
        if geseroff_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), dari_tgl=tgl).exists():
            status = 'ada geseroff'
        else:
            # cek jika absen di tanggal opg tgl tidak ada absen masuk atau absen pulangnya, batalkan
            if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=tgl).exists():
                
                ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=tgl)

                if ab.masuk is None and ab.pulang is None:
                    status = 'pegawai tidak masuk'
                else:
                    if nh == off:
                        topg = opg_db(
                            pegawai_id = int(dpegawai),
                            opg_tgl = tgl,
                            keterangan = 'OFF Pengganti Reguler',
                            add_by = nama_user,
                            edit_by = nama_user
                        )
                        topg.save()
                        
                        status = 'ok'
                    else:
                        if tln is not None:
                            if tln == tgl:
                                topg = opg_db(
                                    pegawai_id = int(dpegawai),
                                    opg_tgl = tgl,
                                    keterangan = 'OFF Pengganti Tgl Merah',
                                    add_by = nama_user,
                                    edit_by = nama_user
                                )
                                topg.save()
                        
                                status = 'ok'
                            else:
                                status = 'bukan tgl merah'
                        else:
                            status = 'bukan off reguler'   
            else:
                status = 'belum ada data absensi'                                 
                                    
    return JsonResponse({"status": status})


@login_required
def pakai_opg(request):
    nama_user = request.user.username
    
    idopg = request.POST.get('id_pakai')
    dtgl = request.POST.get('ptgl')
    
    diambil_tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()
    
    opg = opg_db.objects.get(id=int(idopg))
    idp = opg.pegawai_id
    opg_tgl = datetime.strftime(opg.opg_tgl,'%d-%m-%Y')   
    
    pg = pegawai_db.objects.get(id=int(idp))  
    off = pg.hari_off.hari
    day = diambil_tgl.strftime("%A")
    nh = nama_hari(day) 
            
    if absensi_db.objects.filter(tgl_absen=diambil_tgl, pegawai_id=int(idp)).exists():
        
        ab = absensi_db.objects.get(tgl_absen=diambil_tgl, pegawai_id=int(idp))
        
        if ab.masuk is None and ab.pulang is None:
            if off == nh:
                status = 'hari off'
            else:
                if geseroff_db.objects.filter(pegawai_id=int(idp), ke_tgl=diambil_tgl).exists():
                    status = 'ada geseroff'
                else:        
                    ab.keterangan_absensi = f"OPG-({opg_tgl})"
                    ab.save()
                    
                    opg.diambil_tgl = diambil_tgl
                    opg.status = 1
                    opg.edit_by = nama_user
                    opg.save()
                    
                    status = 'ok'
        else:
            status = 'pegawai masuk'    
                                           
    return JsonResponse({"status": status})


@login_required
def batal_opg(request):
    nama_user = request.user.username
    
    idopg = request.POST.get('id_batal')
    
    opg = opg_db.objects.select_related('pegawai').get(id=int(idopg))
    
    idp = opg.pegawai_id
    tgl = opg.diambil_tgl
    
    ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=tgl)
    ab.keterangan_absensi = None
    ab.save()
    
    opg.diambil_tgl = None
    opg.status = 0
    opg.edit_by = nama_user
    opg.save()
    
    status = 'ok'
                                  
    return JsonResponse({"status": status})


@login_required
def hapus_opg(request):
    nama_user = request.user.username
    
    idopg = request.POST.get('id_hapus')
    
    opg = opg_db.objects.select_related('pegawai').get(id=int(idopg))
    idp = opg.pegawai_id
    nama_pegawai = opg.pegawai.nama
    tgl_ambil = opg.diambil_tgl
    tgl_opg = opg.opg_tgl
    
    if opg.status == 1:
        ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=tgl_ambil)
        ab.keterangan_absensi = None
        ab.save()       
    else:
        pass
    
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"OPG-(a.n {nama_pegawai}, tgl:{tgl_opg})"
    )
    histori.save()    
    
    opg.delete()
        
    status = 'ok'
                                  
    return JsonResponse({"status": status})


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Cuti

@login_required
def cuti(request, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
        dari = pa[0].date()
        sampai = pa[1].date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            'today' : today,
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/Ijins/cuti/cuti.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def detail_cuti(request, sid, idp):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        today = date.today()
        
        pg = pegawai_db.objects.get(id=int(idp))
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')
        
        ac = awal_cuti_db.objects.last()
        tac = ac.tgl       
        
        data = {
            'akses' : akses,
            'idp' : idp,
            'dsid': dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari': tac,
            'sampai': today,
            'nama_pegawai':pg.nama,
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/Ijins/cuti/detail_cuti.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_cuti(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dtgl1 = request.POST.get('ctgl1')
        dtgl2 = request.POST.get('ctgl2')
        idp = request.POST.get('idp')
        
        dari = datetime.strptime(dtgl1,'%d-%m-%Y').date()
        sampai = datetime.strptime(dtgl2,'%d-%m-%Y').date()
        
        pg = pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id      
        
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')
        
        data = {
            'akses' : akses,
            'idp' : idp,
            'dsid': dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari': dari,
            'sampai': sampai,
            'nama_pegawai':pg.nama,
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/Ijins/cuti/detail_cuti.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cuti_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
                       
        if int(sid) == 0:
            for i in cuti_db.objects.select_related('pegawai').filter(tgl_cuti__range=(dari,sampai)):
                
                ct = {
                    'id':i.id,
                    'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'sisa_cuti':i.pegawai.sisa_cuti
                }
                data.append(ct)
        else:
            for i in cuti_db.objects.select_related('pegawai').filter(tgl_cuti__range=(dari,sampai), pegawai__status_id=int(sid)):
                            
                ct = {
                    'id':i.id,
                    'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'sisa_cuti':i.pegawai.sisa_cuti
                }
                data.append(ct)
                               
        return JsonResponse({"data": data})


@login_required
def dcuti_json(request, idp):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        ac = awal_cuti_db.objects.last()
        tac = ac.tgl
        
        for i in cuti_db.objects.select_related('pegawai').filter(tgl_cuti__gte=tac, pegawai_id=int(idp)):
                        
            ct = {
                'id':i.id,
                'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                'ket':i.keterangan,
                'cuti_ke':i.cuti_ke,
                'edit':i.edit_by,
                'etgl':datetime.strftime(i.edit_date, '%d-%m-%Y')
            }
            data.append(ct)
                               
        return JsonResponse({"data": data})


@login_required
def tambah_cuti(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl')
    idp = request.POST.get('idp')
    dket = request.POST.get('ket')
    
    ltgl = dtgl.split(', ')   
    
    ac = awal_cuti_db.objects.last()
    tac = ac.tgl
        
    for t in ltgl:
        tgl = datetime.strptime(t,'%d-%m-%Y').date()
        
        pg = pegawai_db.objects.get(id=int(idp))
        sc = pg.sisa_cuti
        
        ct = cuti_db.objects.filter(pegawai_id=int(idp), tgl_cuti__gte=tac).aggregate(total=Count('id'))
        if ct is None:
            cuti_ke = 1
        else:
            cuti_ke = ct['total'] + 1  
            
        if dket is None:
            ket = f"Cuti ke {cuti_ke}"
        else:          
            ket = f"Cuti ke {cuti_ke}-({dket})"
   
        # tidak boleh ada opg, geseroff, atau ijin lainnya di tgl yang akan dipakai cuti
        if ijin_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_ijin=tgl).exists():
            status = 'ada ijin'
        else:
            if opg_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), diambil_tgl=tgl).exists():
                status = 'ada opg' 
            else:
                if geseroff_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), ke_tgl=tgl).exists():
                    status = 'ada geseroff'
                else:
                    if cuti_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_cuti=tgl).exists():
                        status = 'duplikat'
                    else:
                        if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_absen=tgl).exists():
                            
                            ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(idp), tgl_absen=tgl)
                            
                            if ab.masuk is None and ab.pulang is None:
                                ab.keterangan_absensi = ket
                                ab.save()
                                
                                tcuti = cuti_db(
                                    pegawai_id = int(idp),
                                    tgl_cuti = tgl,
                                    keterangan = dket,
                                    cuti_ke = cuti_ke,
                                    add_by = nama_user,
                                    edit_by = nama_user
                                )               
                                tcuti.save()
                                
                                pg.sisa_cuti = sc - 1
                                pg.save()
                                
                                status = 'ok'
                            else:
                                if ab.masuk is not None and ab.pulang is not None:
                                    if ab.masuk < ab.pulang :
                                        dmsk = f'{ab.tgl_absen} {ab.masuk}'
                                        dplg = f'{ab.tgl_absen} {ab.pulang}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                        selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
                                        
                                        if int(selisih.hour) <= 4:
                                            ab.keterangan_absensi = ket
                                            ab.save()
                                            
                                            tcuti = cuti_db(
                                                pegawai_id = int(idp),
                                                tgl_cuti = tgl,
                                                keterangan = ket,
                                                cuti_ke = cuti_ke,
                                                add_by = nama_user,
                                                edit_by = nama_user
                                            )               
                                            tcuti.save()
                                            
                                            pg.sisa_cuti = sc - 1
                                            pg.save()
                                            
                                            status = 'ok'
                                        else:                                
                                            status = 'pegawai masuk'
                                    else:
                                        tplus = ab.tgl_absen + timedelta(days=1)             
                            
                                        dmsk = f'{ab.tgl_absen} {ab.masuk}'
                                        dplg = f'{tplus} {ab.pulang}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                        selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
                                        
                                        if int(selisih.hour) <= 4: 
                                            ab.keterangan_absensi = ket
                                            ab.save()
                                            
                                            tcuti = cuti_db(
                                                pegawai_id = int(idp),
                                                tgl_cuti = tgl,
                                                keterangan = ket,
                                                cuti_ke = cuti_ke,
                                                add_by = nama_user,
                                                edit_by = nama_user
                                            )               
                                            tcuti.save()
                                            
                                            pg.sisa_cuti = sc - 1
                                            pg.save()
                                            
                                            status = 'ok'
                                        else:
                                            status = 'pegawai masuk'           
                                else:
                                    status = 'pegawai masuk'
                        else:
                            tcuti = cuti_db(
                                pegawai_id = int(idp),
                                tgl_cuti = tgl,
                                keterangan = ket,
                                cuti_ke = cuti_ke,
                                add_by = nama_user,
                                edit_by = nama_user
                            )               
                            tcuti.save()
                            
                            pg.sisa_cuti = sc - 1
                            pg.save()
                            
                            status = 'ok'
                                       
    return JsonResponse({"status": status})


@login_required
def edit_sisa_cuti(request):
    
    nama_user = request.user.username
    
    idp = request.POST.get('idp')
    scuti = request.POST.get('scuti')
    modul = request.POST.get('modul')
    
    if modul == 'ecuti':
        pg = pegawai_db.objects.get(id=int(idp))
        pg.sisa_cuti = int(scuti)
        pg.save()
    elif modul == 'reset_cuti':
        pg = pegawai_db.objects.get(id=int(idp))
        pg.sisa_cuti = 12
        pg.save()   
    else:
        for p in pegawai_db.objects.filter(aktif=1):
            if p.tgl_masuk is None:
                pass
            else:
                pg = pegawai_db.objects.get(id=p.id)
                
                today = date.today()
                tmasuk = pg.tgl_masuk
                
                mkerja = today - tmasuk
                
                # jika sudah lebih dari satu tahun
                if int(mkerja.days) > 360:                
                    pg.sisa_cuti = 12
                    pg.save()        
                else:
                    pass                         
    
    status = 'ok'
    
    return JsonResponse({"status": status})


@login_required
def batal_cuti(request):
    nama_user = request.user.username
    
    idc = request.POST.get('idc')
    
    ct = cuti_db.objects.get(id=int(idc))
    tcuti = ct.tgl_cuti
    idp = ct.pegawai_id
    
    pg = pegawai_db.objects.get(id=idp)
    sc = pg.sisa_cuti
    
    pg.sisa_cuti = sc + 1
    pg.save() 
    
    ab = absensi_db.objects.get(pegawai_id=idp, tgl_absen=tcuti)
    ab.keterangan_absensi = None
    ab.save()
    
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"cuti-(a.n {pg.nama}, tgl:{tcuti})"
    )
    histori.save()   
    
    ct.delete()
    
    status = 'ok'
    
    return JsonResponse({"status": status})


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Lembur

@login_required
def lembur(request, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
        dari = pa[0].date()
        sampai = pa[1].date()
        prd = pa[2]
        thn = pa[3]
        bln = nama_bulan(int(prd))
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        
        lstatus = []
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')
        for s in sid_lembur:
            ds = {
                'id':s.status_pegawai_id,
                'status':s.status_pegawai.status
            }
            lstatus.append(ds)
        
        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                for l in lstatus:
                    if int(sid) == l['id']:
                        data = {
                            'idp':p.id,
                            'nama':p.nama,
                            'nik':p.nik,
                            'userid':p.userid
                        }    
                        pegawai.append(data)
                    else:
                        pass    
            else:
                for l in lstatus:
                    if p.status_id == l['id']:     
                        data = {
                            'idp':p.id,
                            'nama':p.nama,
                            'nik':p.nik,
                            'userid':p.userid
                        }    
                        pegawai.append(data)
                    else:
                        pass    
                        
        data = {
            'akses' : akses,
            'today' : today,
            'status' : lstatus,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'prd':int(prd),
            'thn':int(thn),
            'nama_bulan':bln,
            'modul_aktif' : 'Lembur'
        }
        
        return render(request,'hrd_app/lembur/lembur.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def lembur_belum_proses(request, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
        dari = pa[0].date()
        sampai = pa[1].date()
        prd = pa[2]
        thn = pa[3]
        bln = nama_bulan(int(prd))
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        
        lstatus = []
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')
        for s in sid_lembur:
            ds = {
                'id':s.status_pegawai_id,
                'status':s.status_pegawai.status
            }
            lstatus.append(ds)           

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                for l in lstatus:
                    if int(sid) == l['id']:
                        data = {
                            'idp':p.id,
                            'nama':p.nama,
                            'nik':p.nik,
                            'userid':p.userid
                        }    
                        pegawai.append(data)
                    else:
                        pass    
            else:
                for l in lstatus:
                    if p.status_id == l['id']:     
                        data = {
                            'idp':p.id,
                            'nama':p.nama,
                            'nik':p.nik,
                            'userid':p.userid
                        }    
                        pegawai.append(data)
                    else:
                        pass    
                        
        data = {
            'akses' : akses,
            'today' : today,
            'status' : lstatus,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur.id,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'prd':int(prd),
            'thn':int(thn),
            'nama_bulan':bln,
            'modul_aktif' : 'Lembur'
        }
        
        return render(request,'hrd_app/lembur/belum_proses.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_lembur(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        periode = request.POST.get('periode')
        tahun = request.POST.get('tahun')
        sid = request.POST.get('sid')
        bln = nama_bulan(int(periode))
        
        lstatus = []
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai__status = 'Karyawan Supermarket')
        for s in sid_lembur:
            ds = {
                'id':s.status_pegawai_id,
                'status':s.status_pegawai.status
            }
            lstatus.append(ds)
        
        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                for l in lstatus:
                    if int(sid) == l['id']:
                        data = {
                            'idp':p.id,
                            'nama':p.nama,
                            'nik':p.nik,
                            'userid':p.userid
                        }    
                        pegawai.append(data)
                    else:
                        pass    
            else:
                for l in lstatus:
                    if p.status_id == l['id']:     
                        data = {
                            'idp':p.id,
                            'nama':p.nama,
                            'nik':p.nik,
                            'userid':p.userid
                        }    
                        pegawai.append(data)
                    else:
                        pass    
           
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid' : int(sid),
            'status' : lstatus,
            'pegawai' : pegawai,
            'sil': sid_lembur.id,
            'prd': periode,
            'thn': tahun,
            'nama_bulan':bln,
            'modul_aktif' : 'Lembur'
        }
        
        return render(request,'hrd_app/lembur/cari_lembur.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def tambah_lembur(request):
    nama_user = request.user.username
    
    sid = request.POST.get('sid')
    dtgl = request.POST.get('tgl')
    idp = int(request.POST.get('pegawai'))
    awal = float(request.POST.get('awal'))
    akhir = float(request.POST.get('akhir'))
    ist_1 = float(request.POST.get('ist_1'))
    ist_2 = float(request.POST.get('ist_2'))
   
    tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()
  
    pt = periode_tgl(dtgl)
    dr = pt[0]
    sp = pt[1]
    prd = pt[2]
    thn = pt[3]
    
    b_msk = []
    b_plg = []
    
    b_ist = []
    b_ist2 = []
    s_ist = []    
    
    # define looping
    if awal > 0 and akhir > 0:
        looping = (awal / 0.5) + (akhir / 0.5)
    elif awal > 0 and akhir == 0:       
        looping = (awal / 0.5)
    elif awal == 0 and akhir > 0:
        looping = (akhir / 0.5)                  
                    
    # pengolahan lembur
    if lembur_db.objects.filter(pegawai_id=int(idp), tgl_lembur=tgl).exists():
        messages.info(request, 'Duplikat Data.') 
    else:
        
        # jika absensi ada
        if absensi_db.objects.select_related('pegawai').filter(tgl_absen=tgl, pegawai_id=int(idp)).exists():
            ab = absensi_db.objects.select_related('pegawai').get(tgl_absen=tgl, pegawai_id=int(idp))            
            
            # Tanpa istirahat (di jadwal kerja)
            if ab.jam_istirahat == 0:
                if ab.masuk is not None and ab.pulang is not None:
                    
                    jadwal_masuk = datetime.combine(ab.tgl_absen, ab.jam_masuk)
                    jadwal_pulang = datetime.combine(ab.tgl_absen, ab.jam_pulang)
                      
                    absen_masuk = datetime.combine(ab.tgl_absen, ab.masuk)
                    absen_pulang = datetime.combine(ab.tgl_absen, ab.pulang)
                    
                    bm = jadwal_masuk + timedelta(minutes=4)
                    batas_masuk = datetime.strptime(str(bm), "%Y-%m-%d %H:%M:%S")
                    
                    # lebih jam awal
                    jm = jadwal_masuk - timedelta(minutes=1)
                    batas_lembur = jm - timedelta(hours=awal)                                        
                    
                    if absen_masuk < batas_lembur:
                        dcek_selisih = batas_lembur - absen_masuk
                        fcek_selisih = datetime.strptime(str(dcek_selisih), "%H:%M:%S")
                        cek_selisih = datetime.combine(ab.tgl_absen, fcek_selisih.time())
                        
                        cek_selisih_jam = round(cek_selisih.hour + cek_selisih.minute / 60 + cek_selisih.second / 3600, 2)
                        
                        if cek_selisih_jam >= 0.5:
                            lebih_awal = cek_selisih_jam
                        else:
                            lebih_awal = 0
                    else:    
                        lebih_awal = 0
                            
                    # lebih jam akhir
                    batas_lembur_akhir = jadwal_pulang + timedelta(hours=akhir)  
                    
                    if absen_pulang > batas_lembur_akhir:
                        dcek_selisih_akhir = absen_pulang - batas_lembur_akhir
                        fcek_selisih_akhir = datetime.strptime(str(dcek_selisih_akhir), "%H:%M:%S")
                        cek_selisih_akhir = datetime.combine(ab.tgl_absen, fcek_selisih_akhir.time())
                        
                        cek_selisih_jam_akhir = round(cek_selisih_akhir.hour + cek_selisih_akhir.minute / 60 + cek_selisih_akhir.second / 3600, 2)
                        
                        if cek_selisih_jam_akhir >= 0.5:
                            lebih_akhir = cek_selisih_jam_akhir
                        else:
                            lebih_akhir = 0
                    else:    
                        lebih_akhir = 0
                
                    if awal > 0 and akhir > 0:
                        lebih = lebih_awal + lebih_akhir
                    elif awal > 0 and akhir == 0:     
                        lebih = lebih_awal
                    elif awal == 0 and akhir > 0:
                        lebih = lebih_akhir    
                                          
                    # pengelolaan lembur
                    if lebih == 0:
                        if ab.pulang < ab.masuk:
                            messages.info(request, 'Jam Masuk lebih besar dari Jam Pulang.') 
                        else:
                            # -------------------------------------------------
                            # pemotong jam masuk
                            
                            if awal > 0:
                                mulai_msk = batas_masuk-timedelta(hours=awal)
                            else:
                                mulai_msk = batas_masuk
                                        
                            b_msk.append(mulai_msk)
                                                            
                            for x in range(int(looping) - 1):
                                a2_msk = b_msk[x] + timedelta(minutes=30)
                                b_msk.append(a2_msk)
                            
                            if absen_masuk <= mulai_msk:
                                pemotong_msk = 0
                            else:
                                for b in b_msk:
                                    if absen_masuk > b:
                                        pemotong_msk = (b_msk.index(b) + 1) * 0.5 
                                    else:
                                        pass                     
                            
                            # -------------------------------------------------
                            # pemotong jam istirahat 1 & 2
                            pemotong_ist = 0
                            pemotong_ist2 = 0
                            
                            # -------------------------------------------------
                            # pemotong jam pulang                                
                            
                            if akhir == 0:                                       
                                batas_pulang = jadwal_pulang
                            else:  
                                batas_pulang = jadwal_pulang + timedelta(hours=akhir)                                      
                                
                            mulai_plg = batas_pulang - timedelta(minutes=3)  
                                                                        
                            mulai_plg2 = batas_pulang - timedelta(minutes=35)                                                                                    
                            b_plg.append(mulai_plg2)
                                                            
                            for x in range(int(looping) - 1):
                                a2_plg = b_plg[x] - timedelta(minutes=30)
                                b_plg.append(a2_plg)
                            
                            if absen_pulang >= mulai_plg:
                                pemotong_plg = 0
                            else:
                                if absen_pulang >= mulai_plg2 and absen_pulang < mulai_plg:
                                    pemotong_plg = 0.5
                                else:    
                                    for b in b_plg:
                                        if absen_pulang < b:
                                            pemotong_plg = (b_plg.index(b) + 2) * 0.5
                                        else:
                                            pass                                    
                            
                            # perhitungan lembur
                            if awal > 0 and akhir > 0:
                                lembur = (awal + akhir) - (pemotong_msk + pemotong_ist + pemotong_ist2 + pemotong_plg)
                            elif awal > 0 and akhir == 0:     
                                lembur = (awal) - (pemotong_msk + pemotong_ist + pemotong_ist2 + pemotong_plg)
                            elif awal == 0 and akhir > 0:
                                lembur = (akhir) - (pemotong_msk + pemotong_ist + pemotong_ist2 + pemotong_plg)                    
                        
                            tambah_lembur = lembur_db(
                                pegawai_id = int(idp),
                                tgl_lembur = tgl,       
                                lembur_awal = awal,
                                lembur_akhir = akhir,
                                istirahat = ist_1,
                                istirahat2 = ist_2,
                                proses_lembur = lembur,
                                status = 1,
                                keterangan = '',
                                add_by = nama_user,
                                edit_by = nama_user    
                            )
                            tambah_lembur.save()
                    else: 
                        tambah_lembur = lembur_db(
                            pegawai_id = int(idp),
                            tgl_lembur = tgl,       
                            lembur_awal = awal,
                            lembur_akhir = akhir,
                            istirahat = ist_1,
                            istirahat2 = ist_2,
                            lebih_nproses = lebih,
                            proses_lembur = 0,
                            status = 0,
                            keterangan = f'Terdapat {lebih} jam yang belum diregistrasi.',
                            add_by = nama_user,
                            edit_by = nama_user    
                        )
                        tambah_lembur.save()     
                        return redirect('lembur_bproses', int(sid))             
                                   
                else:
                    messages.info(request, 'Absen Tidak Lengkap.')
       
            # Dengan Istirahat (di jadwal kerja)
            else:
                if ab.masuk is not None and ab.pulang is not None:
                    
                    jadwal_masuk = datetime.combine(ab.tgl_absen, ab.jam_masuk) 
                    jadwal_pulang = datetime.combine(ab.tgl_absen, ab.jam_pulang)
                     
                    absen_masuk = datetime.combine(ab.tgl_absen, ab.masuk)
                    absen_pulang = datetime.combine(ab.tgl_absen, ab.pulang)
                    
                    bm = jadwal_masuk + timedelta(minutes=4)
                    batas_masuk = datetime.strptime(str(bm), "%Y-%m-%d %H:%M:%S")                                                   
                        
                    # lebih jam awal
                    jm = jadwal_masuk - timedelta(minutes=1)
                    batas_lembur = jm - timedelta(hours=awal)  
                    
                    if absen_masuk < batas_lembur:
                        dcek_selisih = batas_lembur - absen_masuk
                        fcek_selisih = datetime.strptime(str(dcek_selisih), "%H:%M:%S")
                        cek_selisih = datetime.combine(ab.tgl_absen, fcek_selisih.time())
                        
                        cek_selisih_jam = round(cek_selisih.hour + cek_selisih.minute / 60 + cek_selisih.second / 3600, 2)
                        
                        if cek_selisih_jam >= 0.5:
                            lebih_awal = cek_selisih_jam
                        else:
                            lebih_awal = 0
                    else:    
                        lebih_awal = 0
                        
                    # lebih jam akhir
                    batas_lembur_akhir = jadwal_pulang + timedelta(hours=akhir)  
                    
                    if absen_pulang > batas_lembur_akhir:
                        dcek_selisih_akhir = absen_pulang - batas_lembur_akhir
                        fcek_selisih_akhir = datetime.strptime(str(dcek_selisih_akhir), "%H:%M:%S")
                        cek_selisih_akhir = datetime.combine(ab.tgl_absen, fcek_selisih_akhir.time())
                        
                        cek_selisih_jam_akhir = round(cek_selisih_akhir.hour + cek_selisih_akhir.minute / 60 + cek_selisih_akhir.second / 3600, 2)
                        
                        if cek_selisih_jam_akhir >= 0.5:
                            lebih_akhir = cek_selisih_jam_akhir
                        else:
                            lebih_akhir = 0
                    else:    
                        lebih_akhir = 0
                
                    if awal > 0 and akhir > 0:
                        lebih = lebih_awal + lebih_akhir
                    elif awal > 0 and akhir == 0:     
                        lebih = lebih_awal
                    elif awal == 0 and akhir > 0:
                        lebih = lebih_akhir    
                     
                    # pengolahan lembur   
                    if lebih == 0:                     
                        if ab.pulang < ab.masuk:
                            messages.info(request, 'Jam Masuk lebih besar dari Jam Pulang.')
                        else:
                            # -------------------------------------------------
                            # pemotong jam masuk
                            
                            if awal > 0:
                                mulai_msk = batas_masuk-timedelta(hours=awal)
                            else:
                                mulai_msk = batas_masuk
                                        
                            b_msk.append(mulai_msk)
                                                            
                            for x in range(int(looping) - 1):
                                a2_msk = b_msk[x] + timedelta(minutes=30)
                                b_msk.append(a2_msk)
                            
                            if absen_masuk <= mulai_msk:
                                pemotong_msk = 0
                            else:
                                for b in b_msk:
                                    if absen_masuk > b:
                                        pemotong_msk = (b_msk.index(b) + 1) * 0.5 
                                    else:
                                        pass                                   
                                
                            # -------------------------------------------------
                            # pemotong jam pulang                                
                            
                            if akhir > 0:                                       
                                batas_pulang = jadwal_pulang + timedelta(hours=akhir)                                      
                            else:  
                                batas_pulang = jadwal_pulang
                                
                            mulai_plg = batas_pulang - timedelta(minutes=3)  
                                                                        
                            mulai_plg2 = batas_pulang - timedelta(minutes=35)                                                                                    
                            b_plg.append(mulai_plg2)
                                                            
                            for x in range(int(looping) - 1):
                                a2_plg = b_plg[x] - timedelta(minutes=30)
                                b_plg.append(a2_plg)
                            
                            if absen_pulang >= mulai_plg:
                                pemotong_plg = 0
                            else:
                                if absen_pulang >= mulai_plg2 and absen_pulang < mulai_plg:
                                    pemotong_plg = 0.5
                                else:    
                                    for b in b_plg:
                                        if absen_pulang < b:
                                            pemotong_plg = (b_plg.index(b) + 2) * 0.5
                                        else:
                                            pass
                                    
                            # -------------------------------------------------
                            # pemotong jam istirahat
                            
                            if ab.istirahat is not None and ab.kembali is not None:
                                
                                absen_ist = datetime.combine(ab.tgl_absen, ab.istirahat)
                                absen_kmb = datetime.combine(ab.tgl_absen, ab.kembali)
                                
                                if ab.istirahat2 is None and ab.kembali2 is None:
                                    if ab.kembali < ab.istirahat:
                                        messages.info(request, 'Jam istirahat lebih besar dari jam kembali istirahat.')
                                    else:                                    
                                        # -------------------------------------------------
                                        # istirahat 1
                                        
                                        lama_ist = (ist_1 * 60) + 5                                     
                                        
                                        a_ist = absen_ist + timedelta(minutes=lama_ist)  
                                        b_ist.append(a_ist)     
                                        
                                        for x in range(int(looping) - 1):
                                            a2_ist = b_ist[x] + timedelta(minutes=30)
                                            b_ist.append(a2_ist)
                                        
                                        if absen_kmb <= a_ist:
                                            pemotong_ist = 0
                                            pemotong_ist2 = 0
                                            s_ist.append(pemotong_ist)
                                        else:
                                            for b in b_ist:                             
                                                if absen_kmb > b:
                                                    pemotong_ist = (b_ist.index(b) + 1) * 0.5  
                                                    pemotong_ist2 = 0 
                                                    s_ist.append(pemotong_ist) 
                                                else:
                                                    pass                                      
                                        
                                else:
                                    # -------------------------------------------------
                                    # istirahat 1
                                    
                                    lama_ist = (ist_1 * 60) + 5                                     
                                    
                                    a_ist = absen_ist + timedelta(minutes=lama_ist)  
                                    b_ist.append(a_ist)     
                                    
                                    for x in range(int(looping) - 1):
                                        a2_ist = b_ist[x] + timedelta(minutes=30)
                                        b_ist.append(a2_ist)
                                    
                                    if absen_kmb <= a_ist:
                                        pemotong_ist = 0
                                        pemotong_ist2 = 0
                                        s_ist.append(pemotong_ist)
                                    else:
                                        for b in b_ist:                             
                                            if absen_kmb > b:
                                                pemotong_ist = (b_ist.index(b) + 1) * 0.5  
                                                pemotong_ist2 = 0 
                                                s_ist.append(pemotong_ist) 
                                            else:
                                                pass 
                                    
                                    if ab.kembali2 < ab.istirahat2:
                                        messages.info(request, 'Jam istirahat 2 lebih besar dari jam kembali istirahat 2.')
                                    else:
                                        # -------------------------------------------------
                                        # istirahat 2
                                        
                                        absen_ist2 = datetime.combine(ab.tgl_absen, ab.istirahat2)
                                        absen_kmb2 = datetime.combine(ab.tgl_absen, ab.kembali2)
                                        
                                        lama_ist2 = (ist_2 * 60) + 5                                     
                                        
                                        a_ist2 = absen_ist2 + timedelta(minutes=lama_ist2)  
                                        b_ist2.append(a_ist2)     
                                        
                                        for x in range(int(looping) - 1):
                                            a2_ist2 = b_ist2[x] + timedelta(minutes=30)
                                            b_ist2.append(a2_ist2)
                                        
                                        if absen_kmb2 <= a_ist2:
                                            pemotong_ist = s_ist[0]
                                            pemotong_ist2 = 0
                                        else:
                                            for b in b_ist2:                             
                                                if absen_kmb2 > b:
                                                    pemotong_ist = s_ist[0]  
                                                    pemotong_ist2 = (b_ist2.index(b) + 1) * 0.5  
                                                else:
                                                    pass                                      
                                    
                            else:                                
                                pemotong_ist = -1
                                pemotong_ist2 = 0

                            # additional perhitungan istirahat
                            if ist_1 + ist_2 > 1:
                                selisih_pi = (ist_1+ist_2) - 1
                                pi = (pemotong_ist + pemotong_ist2) + selisih_pi
                            else:
                                pi = pemotong_ist + pemotong_ist2    
                            
                            # perhitungan lembur
                            if awal > 0 and akhir > 0:
                                lembur = (awal + akhir) - (pemotong_msk + pi + pemotong_plg)
                            elif awal > 0 and akhir == 0:     
                                lembur = (awal) - (pemotong_msk + pi + pemotong_plg)
                            elif awal == 0 and akhir > 0:
                                lembur = (akhir) - (pemotong_msk + pi + pemotong_plg) 
                                
                            tambah_lembur = lembur_db(
                                pegawai_id = int(idp),
                                tgl_lembur = tgl,       
                                lembur_awal = awal,
                                lembur_akhir = akhir,
                                istirahat = ist_1,
                                istirahat2 = ist_2,
                                proses_lembur = lembur,
                                status = 1,
                                keterangan = '',
                                add_by = nama_user,
                                edit_by = nama_user    
                            )
                            tambah_lembur.save()  
                    else:
                        tambah_lembur = lembur_db(
                            pegawai_id = int(idp),
                            tgl_lembur = tgl,       
                            lembur_awal = awal,
                            lembur_akhir = akhir,
                            istirahat = ist_1,
                            istirahat2 = ist_2,
                            lebih_nproses = lebih,
                            proses_lembur = 0,
                            status = 0,
                            keterangan = f'Terdapat {lebih} jam yang belum diregistrasi.',
                            add_by = nama_user,
                            edit_by = nama_user    
                        )
                        tambah_lembur.save()   
                        return redirect('lembur_bproses', int(sid))          
                    
                else:
                    messages.info(request, 'Absen Tidak Lengkap.')
        
        # jika tidak ada absensi
        else:            
            tambah_lembur = lembur_db(
                pegawai_id = int(idp),
                tgl_lembur = tgl,       
                lembur_awal = awal,
                lembur_akhir = akhir,
                istirahat = ist_1,
                istirahat2 = ist_2,
                proses_lembur = 0,
                status = 0,
                keterangan = 'Belum ada data absensi',
                add_by = nama_user,
                edit_by = nama_user    
            )
            tambah_lembur.save()
            return redirect('lembur_bproses', int(sid))

    # insert or update rekap lembur
    # -------------------------------------------------------------
    # hitung total lembur
    tl = lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
    if tl['total'] is None:
        tlembur = 0
    else:
        tlembur = tl['total'] 
    
    # hitung total kompen
    kp = kompen_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
    if kp['total'] is None:
        tkompen = 0
    else:
        tkompen = kp['total']        
        
    if prd == 1:
        prds = 12
        thns = thn - 1
    else:
        prds = prd - 1
        thns = thn    
        
    # hitung sisa lembur
    if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), periode=prds, tahun=thns).exists():
        rkps = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=int(idp), periode=prds, tahun=thns)
        sisa_lembur_sbl = rkps.sisa_lembur
    else:
        sisa_lembur_sbl = 0     
        
    # input or update rekap lembur  
    if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), periode=prd, tahun=thn).exists():
        rk = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=int(idp), periode=prd, tahun=thn)
        
        rk.total_lembur = float(sisa_lembur_sbl + tlembur)
        rk.total_kompen = float(tkompen)
        rk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(rk.lembur_jam_bayar)
        rk.edit_by = nama_user          
        rk.save()
    else:  
        tambah_rekap = rekap_lembur_db(
            pegawai_id = int(idp),
            periode = prd,
            tahun = thn,
            total_lembur = float(sisa_lembur_sbl) + float(tlembur),
            total_kompen = float(tkompen),
            sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen),
            add_by = nama_user,
            edit_by = nama_user
        )    
        tambah_rekap.save()
    
    return redirect('lembur', int(sid))

@login_required
def proses_ulang_lembur(request, idl):
    nama_user = request.user.username
    
    lb = lembur_db.objects.get(id=int(idl))
    
    sid = lb.pegawai.status_id
    dtgl = lb.tgl_lembur
    idp = lb.pegawai_id
    awal = float(lb.lembur_awal)
    akhir = float(lb.lembur_akhir)
    ist_1 = float(lb.istirahat)
    ist_2 = float(lb.istirahat2)
   
    ftgl = datetime.strftime(dtgl,'%d-%m-%Y')
    tgl = dtgl
  
    pt = periode_tgl(ftgl)
    dr = pt[0]
    sp = pt[1]
    prd = pt[2]
    thn = pt[3]
    
    b_msk = []
    b_plg = []
    
    b_ist = []
    b_ist2 = []
    s_ist = []    
    
    # define looping
    if awal > 0 and akhir > 0:
        looping = (awal / 0.5) + (akhir / 0.5)
    elif awal > 0 and akhir == 0:       
        looping = (awal / 0.5)
    elif awal == 0 and akhir > 0:
        looping = (akhir / 0.5)                  
                    
    # pengolahan lembur
    # ------------------------------------------------------------- 
    # jika absensi ada
    if absensi_db.objects.select_related('pegawai').filter(tgl_absen=tgl, pegawai_id=int(idp)).exists():
        ab = absensi_db.objects.select_related('pegawai').get(tgl_absen=tgl, pegawai_id=int(idp))            
        
        # Tanpa istirahat (di jadwal kerja)
        if ab.jam_istirahat == 0:
            if ab.masuk is not None and ab.pulang is not None:
                
                jadwal_masuk = datetime.combine(ab.tgl_absen, ab.jam_masuk)
                jadwal_pulang = datetime.combine(ab.tgl_absen, ab.jam_pulang)
                    
                absen_masuk = datetime.combine(ab.tgl_absen, ab.masuk)
                absen_pulang = datetime.combine(ab.tgl_absen, ab.pulang)
                
                bm = jadwal_masuk + timedelta(minutes=4)
                batas_masuk = datetime.strptime(str(bm), "%Y-%m-%d %H:%M:%S")            
                                        
                # pengelolaan lembur
                if ab.pulang < ab.masuk:
                    messages.info(request, 'Jam Masuk lebih besar dari Jam Pulang.') 
                else:
                    # -------------------------------------------------
                    # pemotong jam masuk
                    
                    if awal > 0:
                        mulai_msk = batas_masuk-timedelta(hours=awal)
                    else:
                        mulai_msk = batas_masuk
                                
                    b_msk.append(mulai_msk)
                                                    
                    for x in range(int(looping) - 1):
                        a2_msk = b_msk[x] + timedelta(minutes=30)
                        b_msk.append(a2_msk)
                    
                    if absen_masuk <= mulai_msk:
                        pemotong_msk = 0
                    else:
                        for b in b_msk:
                            if absen_masuk > b:
                                pemotong_msk = (b_msk.index(b) + 1) * 0.5 
                            else:
                                pass                     
                    
                    # -------------------------------------------------
                    # pemotong jam istirahat 1 & 2
                    pemotong_ist = 0
                    pemotong_ist2 = 0
                    
                    # -------------------------------------------------
                    # pemotong jam pulang                                
                    
                    if akhir == 0:                                       
                        batas_pulang = jadwal_pulang
                    else:  
                        batas_pulang = jadwal_pulang + timedelta(hours=akhir)                                      
                        
                    mulai_plg = batas_pulang - timedelta(minutes=3)  
                                                                
                    mulai_plg2 = batas_pulang - timedelta(minutes=35)                                                                                    
                    b_plg.append(mulai_plg2)
                                                    
                    for x in range(int(looping) - 1):
                        a2_plg = b_plg[x] - timedelta(minutes=30)
                        b_plg.append(a2_plg)
                    
                    if absen_pulang >= mulai_plg:
                        pemotong_plg = 0
                    else:
                        if absen_pulang >= mulai_plg2 and absen_pulang < mulai_plg:
                            pemotong_plg = 0.5
                        else:    
                            for b in b_plg:
                                if absen_pulang < b:
                                    pemotong_plg = (b_plg.index(b) + 2) * 0.5
                                else:
                                    pass                                    
                    
                    # perhitungan lembur
                    if awal > 0 and akhir > 0:
                        lembur = (awal + akhir) - (pemotong_msk + pemotong_ist + pemotong_ist2 + pemotong_plg)
                    elif awal > 0 and akhir == 0:     
                        lembur = (awal) - (pemotong_msk + pemotong_ist + pemotong_ist2 + pemotong_plg)
                    elif awal == 0 and akhir > 0:
                        lembur = (akhir) - (pemotong_msk + pemotong_ist + pemotong_ist2 + pemotong_plg)                    
                
                    lb.status = 1
                    lb.keterangan = ''
                    lb.proses_lembur = lembur
                    
                    if lb.lebih_nproses > 0: 
                        lb.keterangan = 'Diproses tanpa menambahkan kelebihan jam'
                    else:
                        lb.keterangan = ''
                            
                    lb.edit_by = nama_user
                    lb.save()                        
                                
            else:
                messages.info(request, 'Absen Tidak Lengkap.')
    
        # Dengan Istirahat (di jadwal kerja)
        else:
            if ab.masuk is not None and ab.pulang is not None:
                
                jadwal_masuk = datetime.combine(ab.tgl_absen, ab.jam_masuk) 
                jadwal_pulang = datetime.combine(ab.tgl_absen, ab.jam_pulang)
                    
                absen_masuk = datetime.combine(ab.tgl_absen, ab.masuk)
                absen_pulang = datetime.combine(ab.tgl_absen, ab.pulang)
                
                bm = jadwal_masuk + timedelta(minutes=4)
                batas_masuk = datetime.strptime(str(bm), "%Y-%m-%d %H:%M:%S")
                    
                # pengolahan lembur                
                if ab.pulang < ab.masuk:
                    messages.info(request, 'Jam Masuk lebih besar dari Jam Pulang.')
                else:
                    # -------------------------------------------------
                    # pemotong jam masuk
                    
                    if awal > 0:
                        mulai_msk = batas_masuk-timedelta(hours=awal)
                    else:
                        mulai_msk = batas_masuk
                                
                    b_msk.append(mulai_msk)
                                                    
                    for x in range(int(looping) - 1):
                        a2_msk = b_msk[x] + timedelta(minutes=30)
                        b_msk.append(a2_msk)
                    
                    if absen_masuk <= mulai_msk:
                        pemotong_msk = 0
                    else:
                        for b in b_msk:
                            if absen_masuk > b:
                                pemotong_msk = (b_msk.index(b) + 1) * 0.5 
                            else:
                                pass                                   
                        
                    # -------------------------------------------------
                    # pemotong jam pulang                                
                    
                    if akhir > 0:                                       
                        batas_pulang = jadwal_pulang + timedelta(hours=akhir)                                      
                    else:  
                        batas_pulang = jadwal_pulang
                        
                    mulai_plg = batas_pulang - timedelta(minutes=3)  
                                                                
                    mulai_plg2 = batas_pulang - timedelta(minutes=35)                                                                                    
                    b_plg.append(mulai_plg2)
                                                    
                    for x in range(int(looping) - 1):
                        a2_plg = b_plg[x] - timedelta(minutes=30)
                        b_plg.append(a2_plg)
                    
                    if absen_pulang >= mulai_plg:
                        pemotong_plg = 0
                    else:
                        if absen_pulang >= mulai_plg2 and absen_pulang < mulai_plg:
                            pemotong_plg = 0.5
                        else:    
                            for b in b_plg:
                                if absen_pulang < b:
                                    pemotong_plg = (b_plg.index(b) + 2) * 0.5
                                else:
                                    pass
                            
                    # -------------------------------------------------
                    # pemotong jam istirahat
                    
                    if ab.istirahat is not None and ab.kembali is not None:
                        
                        absen_ist = datetime.combine(ab.tgl_absen, ab.istirahat)
                        absen_kmb = datetime.combine(ab.tgl_absen, ab.kembali)
                        
                        if ab.istirahat2 is None and ab.kembali2 is None:
                            if ab.kembali < ab.istirahat:
                                messages.info(request, 'Jam istirahat lebih besar dari jam kembali istirahat.')
                            else:                                    
                                # -------------------------------------------------
                                # istirahat 1
                                
                                lama_ist = (ist_1 * 60) + 5                                     
                                
                                a_ist = absen_ist + timedelta(minutes=lama_ist)  
                                b_ist.append(a_ist)     
                                
                                for x in range(int(looping) - 1):
                                    a2_ist = b_ist[x] + timedelta(minutes=30)
                                    b_ist.append(a2_ist)
                                
                                if absen_kmb <= a_ist:
                                    pemotong_ist = 0
                                    pemotong_ist2 = 0
                                    s_ist.append(pemotong_ist)
                                else:
                                    for b in b_ist:                             
                                        if absen_kmb > b:
                                            pemotong_ist = (b_ist.index(b) + 1) * 0.5  
                                            pemotong_ist2 = 0 
                                            s_ist.append(pemotong_ist) 
                                        else:
                                            pass                                      
                                
                        else:
                            # -------------------------------------------------
                            # istirahat 1
                            
                            lama_ist = (ist_1 * 60) + 5                                     
                            
                            a_ist = absen_ist + timedelta(minutes=lama_ist)  
                            b_ist.append(a_ist)     
                            
                            for x in range(int(looping) - 1):
                                a2_ist = b_ist[x] + timedelta(minutes=30)
                                b_ist.append(a2_ist)
                            
                            if absen_kmb <= a_ist:
                                pemotong_ist = 0
                                pemotong_ist2 = 0
                                s_ist.append(pemotong_ist)
                            else:
                                for b in b_ist:                             
                                    if absen_kmb > b:
                                        pemotong_ist = (b_ist.index(b) + 1) * 0.5  
                                        pemotong_ist2 = 0 
                                        s_ist.append(pemotong_ist) 
                                    else:
                                        pass 
                            
                            if ab.kembali2 < ab.istirahat2:
                                messages.info(request, 'Jam istirahat 2 lebih besar dari jam kembali istirahat 2.')
                            else:
                                # -------------------------------------------------
                                # istirahat 2
                                
                                absen_ist2 = datetime.combine(ab.tgl_absen, ab.istirahat2)
                                absen_kmb2 = datetime.combine(ab.tgl_absen, ab.kembali2)
                                
                                lama_ist2 = (ist_2 * 60) + 5                                     
                                
                                a_ist2 = absen_ist2 + timedelta(minutes=lama_ist2)  
                                b_ist2.append(a_ist2)     
                                
                                for x in range(int(looping) - 1):
                                    a2_ist2 = b_ist2[x] + timedelta(minutes=30)
                                    b_ist2.append(a2_ist2)
                                
                                if absen_kmb2 <= a_ist2:
                                    pemotong_ist = s_ist[0]
                                    pemotong_ist2 = 0
                                else:
                                    for b in b_ist2:                             
                                        if absen_kmb2 > b:
                                            pemotong_ist = s_ist[0]  
                                            pemotong_ist2 = (b_ist2.index(b) + 1) * 0.5  
                                        else:
                                            pass                                      
                            
                    else:                                
                        pemotong_ist = -1
                        pemotong_ist2 = 0

                    # additional perhitungan istirahat
                    if ist_1 + ist_2 > 1:
                        selisih_pi = (ist_1+ist_2) - 1
                        pi = (pemotong_ist + pemotong_ist2) + selisih_pi
                    else:
                        pi = pemotong_ist + pemotong_ist2    
                    
                    # perhitungan lembur
                    if awal > 0 and akhir > 0:
                        lembur = (awal + akhir) - (pemotong_msk + pi + pemotong_plg)
                    elif awal > 0 and akhir == 0:     
                        lembur = (awal) - (pemotong_msk + pi + pemotong_plg)
                    elif awal == 0 and akhir > 0:
                        lembur = (akhir) - (pemotong_msk + pi + pemotong_plg) 
                        
                    lb.status = 1
                    lb.proses_lembur = lembur
                    if lb.lebih_nproses > 0:
                        lb.keterangan = 'Diproses tanpa menambahkan kelebihan jam' 
                    else:
                        lb.keterangan = ''
                    lb.edit_by = nama_user
                    lb.save()             
            else:
                messages.info(request, 'Absen Tidak Lengkap.')
    
    # jika tidak ada absensi
    else:   
        return redirect('lembur_bproses', int(sid))

    # insert or update rekap lembur
    # -------------------------------------------------------------
    # hitung total lembur
    tl = lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
    if tl['total'] is None:
        tlembur = 0
    else:
        tlembur = tl['total']    
    
    # hitung total kompen
    kp = kompen_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
    if kp['total'] is None:
        tkompen = 0
    else:
        tkompen = kp['total']        
        
    if prd == 1:
        prds = 12
        thns = thn - 1
    else:
        prds = prd - 1
        thns = thn    
        
    # hitung sisa lembur
    if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), periode=prds, tahun=thns).exists():
        rkps = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=int(idp), periode=prds, tahun=thns)
        sisa_lembur_sbl = rkps.sisa_lembur
    else:
        sisa_lembur_sbl = 0     
        
    # input or update rekap lembur  
    if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), periode=prd, tahun=thn).exists():
        rk = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=int(idp), periode=prd, tahun=thn)
        
        rk.total_lembur = float(sisa_lembur_sbl + tlembur)
        rk.total_kompen = float(tkompen)
        rk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(rk.lembur_jam_bayar)
        rk.edit_by = nama_user          
        rk.save()
    else:  
        tambah_rekap = rekap_lembur_db(
            pegawai_id = int(idp),
            periode = prd,
            tahun = thn,
            total_lembur = float(sisa_lembur_sbl) + float(tlembur),
            total_kompen = float(tkompen),
            sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen),
            add_by = nama_user,
            edit_by = nama_user
        )    
        tambah_rekap.save()
    
    return redirect('lembur', int(sid))


@login_required
def batal_lembur(request):
    nama_user = request.user.username
    
    idl = request.POST.get('id')
    
    lb = lembur_db.objects.get(id=int(idl))
    pg = pegawai_db.objects.get(id=lb.pegawai_id)
    idp = pg.id
    
    ftgl = datetime.strftime(lb.tgl_lembur,'%d-%m-%Y')
  
    pt = periode_tgl(ftgl)
    dr = pt[0]
    sp = pt[1]
    prd = pt[2]
    thn = pt[3]
    
    if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=idp, periode=prd, tahun=thn).exists():
        drk = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=idp, periode=prd, tahun=thn)
        sisa_lembur_sekarang = drk.sisa_lembur
        lembur_sekarang = lb.proses_lembur
    
        if lembur_sekarang > sisa_lembur_sekarang:
            status = 'batalkan kompen'
        else:    
        
            histori = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f"lembur-(a.n {pg.nama}, tgl:{lb.tgl_lembur})"
            )
            histori.save()   
            
            lb.delete()    
        
            # insert or update rekap lembur
            # -------------------------------------------------------------
            # hitung total lembur
            tl = lembur_db.objects.select_related('pegawai').filter(pegawai_id=idp, tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
            if tl['total'] is None:
                tlembur = 0
            else:
                tlembur = tl['total']    
            
            # hitung total kompen
            kp = kompen_db.objects.select_related('pegawai').filter(pegawai_id=idp, tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
            if kp['total'] is None:
                tkompen = 0
            else:
                tkompen = kp['total']        
                
            if prd == 1:
                prds = 12
                thns = thn - 1
            else:
                prds = prd - 1
                thns = thn    
                
            # hitung sisa lembur periode sebelumnya
            if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=idp, periode=prds, tahun=thns).exists():
                rkps = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=idp, periode=prds, tahun=thns)
                sisa_lembur_sbl = rkps.sisa_lembur
            else:
                sisa_lembur_sbl = 0     
                                
            drk.total_lembur = float(sisa_lembur_sbl) + float(tlembur)
            drk.total_kompen = float(tkompen)
            drk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(drk.lembur_jam_bayar)
            drk.edit_by = nama_user
            drk.save()        
                    
            status = 'ok'
    else:
        histori = histori_hapus_db(
            delete_by = nama_user,
            delete_item = f"lembur-(a.n {pg.nama}, tgl:{lb.tgl_lembur})"
        )
        histori.save()   
        
        lb.delete()   
        
        status = 'ok' 
            
    return JsonResponse({"status": status})


@login_required
def bayar_lembur(request):
    nama_user = request.user.username
    
    idr = request.POST.get('idr')
    blembur = request.POST.get('blembur')
    
    rk = rekap_lembur_db.objects.get(id=int(idr))
    pg = pegawai_db.objects.get(id=rk.pegawai_id)
    idp = pg.id        
    
    drpl = rp_lembur_db.objects.last()      
    rp_lembur = drpl.rupiah
    
    pa = periode_absen(rk.periode,rk.tahun)
    dr = pa[0].date()
    sp = pa[1].date()
    prd = pa[2]
    thn = pa[3]  
            
    # insert or update rekap lembur
    # -------------------------------------------------------------
    # hitung total lembur
    tl = lembur_db.objects.select_related('pegawai').filter(pegawai_id=idp, tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
    if tl['total'] is None:
        tlembur = 0
    else:
        tlembur = tl['total']    
    
    # hitung total kompen
    kp = kompen_db.objects.select_related('pegawai').filter(pegawai_id=idp, tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
    if kp['total'] is None:
        tkompen = 0
    else:
        tkompen = kp['total']        
        
    if prd == 1:
        prds = 12
        thns = thn - 1
    else:
        prds = prd - 1
        thns = thn    
        
    # hitung sisa lembur periode sebelumnya
    if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=idp, periode=prds, tahun=thns).exists():
        rkps = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=idp, periode=prds, tahun=thns)
        sisa_lembur_sbl = rkps.sisa_lembur
    else:
        sisa_lembur_sbl = 0        
        
    if float(tkompen) == 0:
        if float(blembur) > float(tlembur):
            status = 'lebih bayar'
        else:   
            # update rekap lembur            
            rk.total_lembur = float(sisa_lembur_sbl + tlembur)
            rk.total_kompen = float(tkompen)
            rk.lembur_jam_bayar = float(blembur)
            rk.lembur_rupiah_bayar = float(blembur) * rp_lembur
            rk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(blembur)
            rk.edit_by = nama_user          
            rk.save()
            status = 'ok'     
    else:    
        if float(blembur) > float(rk.sisa_lembur):
            status = 'lebih bayar'
        else:
            # update rekap lembur            
            rk.total_lembur = float(sisa_lembur_sbl + tlembur)
            rk.total_kompen = float(tkompen)
            rk.lembur_jam_bayar = float(blembur)
            rk.lembur_rupiah_bayar = float(blembur) * rp_lembur
            rk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(blembur)
            rk.edit_by = nama_user 
            rk.save()           
            status = 'ok'
    
    return JsonResponse({"status": status})


@login_required
def rekap_lembur_json(request, sid, prd, thn):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        if rekap_lembur_db.objects.select_related('pegawai').filter(periode=int(prd), tahun=int(thn)).exists():
        
            for r in rekap_lembur_db.objects.select_related('pegawai').filter(periode=int(prd), tahun=int(thn), sisa_lembur__gt=0).order_by('pegawai__divisi__divisi','pegawai__nik'):
                
                if sid == 0:                    
                    rkp = {
                        'id':r.id,
                        'idp':r.pegawai_id,
                        'nama':r.pegawai.nama,
                        'nik':r.pegawai.nik,
                        'userid':r.pegawai.userid,
                        'divisi':r.pegawai.divisi.divisi,
                        'lembur':r.total_lembur,
                        'kompen':r.total_kompen,
                        'sisa':r.sisa_lembur,
                        'bayar':r.lembur_jam_bayar,
                        'prd':prd,
                        'thn':thn
                    }
                    data.append(rkp)
                else:
                    if sid == r.pegawai.status_id:
                        rkp = {
                            'id':r.id,
                            'idp':r.pegawai_id,
                            'nama':r.pegawai.nama,
                            'nik':r.pegawai.nik,
                            'userid':r.pegawai.userid,
                            'divisi':r.pegawai.divisi.divisi,
                            'lembur':r.total_lembur,
                            'kompen':r.total_kompen,
                            'sisa':r.sisa_lembur,
                            'bayar':r.lembur_jam_bayar,
                            'prd':prd,
                            'thn':thn
                        }
                        data.append(rkp)  
                    else:
                        pass      
        else:
            pass        
                               
        return JsonResponse({"data": data})


@login_required
def lembur_belum_proses_json(request, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest": 
        
        data = []
        
        for l in lembur_db.objects.select_related('pegawai').filter(status=0).order_by('tgl_lembur','pegawai__divisi__divisi','pegawai__nik'):
            if sid == 0:
                lbr = {
                    'id':l.id,
                    'nama':l.pegawai.nama,
                    'nik':l.pegawai.nik,
                    'userid':l.pegawai.userid,
                    'divisi':l.pegawai.divisi.divisi,
                    'tgl':datetime.strftime(l.tgl_lembur,'%d-%m-%Y'),
                    'awal':l.lembur_awal,
                    'akhir':l.lembur_akhir,
                    'ist1':l.istirahat,
                    'ist2':l.istirahat2,
                    'total':l.lembur_awal + l.lembur_akhir,
                    'lebih':l.lebih_nproses,
                    'ket':l.keterangan
                }
                data.append(lbr)
            else:
                if sid == l.pegawai.status_id: 
                    lbr = {
                        'id':l.id,
                        'nama':l.pegawai.nama,
                        'nik':l.pegawai.nik,
                        'userid':l.pegawai.userid,
                        'divisi':l.pegawai.divisi.divisi,
                        'tgl':datetime.strftime(l.tgl_lembur,'%d-%m-%Y'),
                        'awal':l.lembur_awal,
                        'akhir':l.lembur_akhir,
                        'ist1':l.istirahat,
                        'ist2':l.istirahat2,
                        'total':l.lembur_awal + l.lembur_akhir,
                        'lebih':l.lebih_nproses,
                        'ket':l.keterangan
                    }
                    data.append(lbr)   
                                
        return JsonResponse({"data": data})


@login_required
def lembur_json(request, idp, prd, thn):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest": 
        
        data = []
        
        pa = periode_absen(prd,thn)
        dr = pa[0].date()
        sp = pa[1].date()
        
        for l in lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_lembur__range=(dr,sp), status=1).order_by('tgl_lembur'):
            lbr = {
                'id':l.id,
                'tgl':datetime.strftime(l.tgl_lembur,'%d-%m-%Y'),
                'lembur':l.proses_lembur,
                'addby':l.add_by,
                'editby':l.edit_by,
                'addtime':datetime.strftime(l.add_date,'%d-%m-%Y %H:%M:%S'),
                'edittime':datetime.strftime(l.edit_date,'%d-%m-%Y %H:%M:%S')
            }
            data.append(lbr)   
                                
        return JsonResponse({"data": data})


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Kompen / PJK

@login_required
def tambah_kompen(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl_kompen')
    idp = request.POST.get('idp')
    jenis = request.POST.get('jkompen')
    kompen = float(request.POST.get('kompen'))
   
    tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()
    ftgl = datetime.strftime(tgl,'%d-%m-%Y')
      
    pt = periode_tgl(ftgl)
    dr = pt[0]
    sp = pt[1]
    prd = pt[2]
    thn = pt[3]   
    
    rkp = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=int(idp), periode=prd, tahun=thn)
    sisa_lembur = rkp.sisa_lembur
    
    if kompen > sisa_lembur:
        status = 'lebih kompen'
    else:    
        
        # update absensi
        if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_absen=tgl).exists():
            ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(idp), tgl_absen=tgl)
            
            jm = datetime.combine(ab.tgl_absen,ab.jam_masuk)
            jp = datetime.combine(ab.tgl_absen,ab.jam_pulang)
            
            njm = jm + timedelta(hours=kompen)
            njp = jp - timedelta(hours=kompen)
            
            # total jam kerja         
            if ab.masuk is not None and ab.pulang is not None:
                if ab.pulang > ab.masuk:
                    
                    dmsk = f'{ab.tgl_absen} {ab.masuk}'
                    dplg = f'{ab.tgl_absen} {ab.pulang}'
                    
                    msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                    plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih = plg - msk
                    djam_selisih = f'{ab.tgl_absen} {dselisih}'
                    selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
                    
                    if int(selisih.hour) <= 4:
                        tjk = 0
                    else:
                        detik = selisih.second / 3600
                        menit = selisih.minute / 60
                        hour = selisih.hour
                        
                        jam = int(hour) + float(menit) + float(detik)
                        
                        tjk = jam       
                    
                    status = 'ok'                
                else: 
                    
                    status = 'Jam masuk > Jam Pulang'                
            else:
                tjk = 0
                status = 'ok'
        
            if jenis == 'awal':
                jm_baru = njm.time()
                jp_baru = ab.jam_pulang
                ket = f'Kompen/PJK-Awal {kompen} Jam'
            elif jenis == 'akhir':
                jm_baru = ab.jam_masuk
                jp_baru = njp.time()
                ket = f'Kompen/PJK-Akhir {kompen} Jam'
            else:
                jm_baru = njm.time()
                jp_baru = njp.time()
                ket = f'Kompen/PJK 1 Hari'            
        
            ab.jam_masuk = jm_baru
            ab.jam_pulang = jp_baru
            ab.keterangan_lain = ket
            ab.total_jam_kerja = round(tjk,1)
            ab.edit_by = nama_user
            ab.save()
            
        # insert kompen
        if kompen_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_kompen = tgl).exists():
            status = 'duplikat'
        else:
            tkompen = kompen_db(
                pegawai_id = int(idp),
                tgl_kompen = tgl,            
                kompen = kompen,
                jenis_kompen = jenis,
                add_by = nama_user,
                edit_by = nama_user
            )   
            tkompen.save() 
        
        # insert or update rekap lembur
        # -------------------------------------------------------------
        # hitung total lembur
        tl = lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
        if tl['total'] is None:
            tlembur = 0
        else:
            tlembur = tl['total']    
        
        # hitung total kompen
        kp = kompen_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
        if kp['total'] is None:
            tkompen = 0
        else:
            tkompen = kp['total']        
            
        if prd == 1:
            prds = 12
            thns = thn - 1
        else:
            prds = prd - 1
            thns = thn    
            
        # hitung sisa lembur
        if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), periode=prds, tahun=thns).exists():
            rkps = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=int(idp), periode=prds, tahun=thns)
            sisa_lembur_sbl = rkps.sisa_lembur
        else:
            sisa_lembur_sbl = 0     
            
        if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), periode=prd, tahun=thn).exists():     
            
            rkp.total_lembur = float(sisa_lembur_sbl + tlembur)
            rkp.total_kompen = float(tkompen)
            rkp.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(rkp.lembur_jam_bayar)
            rkp.edit_by = nama_user          
            rkp.save()     
        else:
            tambah_rekap = rekap_lembur_db(
                pegawai_id = int(idp),
                periode = prd,
                tahun = thn,
                total_lembur = float(sisa_lembur_sbl) + float(tlembur),
                total_kompen = float(tkompen),
                sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen),
                add_by = nama_user,
                edit_by = nama_user
            )    
            tambah_rekap.save()
        
        status = 'ok'
    
    return JsonResponse({"status": status})


@login_required
def batal_kompen(request):
    nama_user = request.user.username
    
    idk = request.POST.get('id')
    
    kp = kompen_db.objects.get(id=int(idk))
    pg = pegawai_db.objects.get(id=kp.pegawai_id)
    idp = pg.id
    
    ftgl = datetime.strftime(kp.tgl_kompen,'%d-%m-%Y')
  
    pt = periode_tgl(ftgl)
    dr = pt[0]
    sp = pt[1]
    prd = pt[2]
    thn = pt[3]   
    
    ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(idp), tgl_absen=kp.tgl_kompen)
        
    jm = datetime.combine(ab.tgl_absen,ab.jam_masuk)
    jp = datetime.combine(ab.tgl_absen,ab.jam_pulang)
    
    jkompen = float(kp.kompen)
    
    if kp.jenis_kompen == 'awal':
        njm = jm - timedelta(hours=jkompen)
        njp = ab.jam_pulang
    elif kp.jenis_kompen == 'akhir':    
        njm = ab.jam_masuk
        njp = jp + timedelta(hours=jkompen)
    else:    
        njm = jm - timedelta(hours=jkompen)
        njp = jp + timedelta(hours=jkompen)
    
    # total jam kerja         
    if ab.masuk is not None and ab.pulang is not None:
        if ab.pulang > ab.masuk:
            
            dmsk = f'{ab.tgl_absen} {ab.masuk}'
            dplg = f'{ab.tgl_absen} {ab.pulang}'
            
            msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
            plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
            
            dselisih = plg - msk
            djam_selisih = f'{ab.tgl_absen} {dselisih}'
            selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
            
            if int(selisih.hour) <= 4:
                tjk = 0
            else:
                detik = selisih.second / 3600
                menit = selisih.minute / 60
                hour = selisih.hour
                
                jam = int(hour) + float(menit) + float(detik)
                
                tjk = jam       
            
            status = 'ok'                
        else: 
            
            status = 'Jam masuk > Jam Pulang'                
    else:
        tjk = 0
        status = 'ok'

    ab.jam_masuk = njm
    ab.jam_pulang = njp
    ab.keterangan_lain = None
    ab.total_jam_kerja = round(tjk,1)
    ab.edit_by = nama_user
    ab.save()
    
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"kompen-(a.n {pg.nama}, tgl:{kp.tgl_kompen})"
    )
    histori.save()   
    
    kp.delete()    

    # insert or update rekap lembur
    # -------------------------------------------------------------
    # hitung total lembur
    tl = lembur_db.objects.select_related('pegawai').filter(pegawai_id=idp, tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
    if tl['total'] is None:
        tlembur = 0
    else:
        tlembur = tl['total']    
    
    # hitung total kompen
    kp = kompen_db.objects.select_related('pegawai').filter(pegawai_id=idp, tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
    if kp['total'] is None:
        tkompen = 0
    else:
        tkompen = kp['total']        
        
    if prd == 1:
        prds = 12
        thns = thn - 1
    else:
        prds = prd - 1
        thns = thn    
        
    # hitung sisa lembur periode sebelumnya
    if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=idp, periode=prds, tahun=thns).exists():
        rkps = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=idp, periode=prds, tahun=thns)
        sisa_lembur_sbl = rkps.sisa_lembur
    else:
        sisa_lembur_sbl = 0     
        
    if rekap_lembur_db.objects.select_related('pegawai').filter(pegawai_id=idp, periode=prd, tahun=thn).exists():           
            
        rkp = rekap_lembur_db.objects.select_related('pegawai').get(pegawai_id=idp, periode=prd, tahun=thn)
          
        rkp.total_lembur = float(sisa_lembur_sbl + tlembur)
        rkp.total_kompen = float(tkompen)
        rkp.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(rkp.lembur_jam_bayar)
        rkp.edit_by = nama_user          
        rkp.save()       
    else:
        tambah_rekap = rekap_lembur_db(
            pegawai_id = int(idp),
            periode = prd,
            tahun = thn,
            total_lembur = float(sisa_lembur_sbl) + float(tlembur),
            total_kompen = float(tkompen),
            sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen),
            add_by = nama_user,
            edit_by = nama_user
        )    
        tambah_rekap.save()
            
    status = 'ok'

    return JsonResponse({"status": status})


@login_required
def kompen_json(request, idp, prd, thn):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest": 
        
        data = []
        
        pa = periode_absen(prd,thn)
        dr = pa[0].date()
        sp = pa[1].date()
        
        for l in kompen_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_kompen__range=(dr,sp)).order_by('tgl_kompen'):
            kmp = {
                'id':l.id,
                'tgl':datetime.strftime(l.tgl_kompen,'%d-%m-%Y'),
                'kompen':l.kompen,
                'jenis':l.jenis_kompen,
                'addby':l.add_by,
                'editby':l.edit_by,
                'addtime':datetime.strftime(l.add_date,'%d-%m-%Y %H:%M:%S'),
                'edittime':datetime.strftime(l.edit_date,'%d-%m-%Y %H:%M:%S')
            }
            data.append(kmp)   
                                
        return JsonResponse({"data": data})


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Pengaturan

@login_required
def pengaturan(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,  
            'modul_aktif' : 'Admin Panel'   
        }
        
        return render(request,'hrd_app/pengaturan/admin_panel.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

# Status Pegawai
# ++++++++++++++
@login_required
def status_pegawai(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Status Pegawai'     
        }
        
        return render(request,'hrd_app/pengaturan/status_pegawai.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def status_pegawai_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in status_pegawai_db.objects.all().order_by('id'):
            
            sp = {
                'id':i.id,
                'status':i.status,
            }
            data.append(sp)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_status_pegawai(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dstatus = request.POST.get('status')
        
        if status_pegawai_db.objects.filter(status = dstatus).exists():
            status = 'duplikat'
        else:    
            tstatus = status_pegawai_db(
                status = dstatus
            )
            tstatus.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_status_pegawai(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        dstatus = request.POST.get('estatus')
        
        if status_pegawai_db.objects.filter(status = dstatus).exists():
            status = 'duplikat'
        else:    
            nstatus = status_pegawai_db.objects.get(id=int(eid))
            nstatus.status = dstatus
            nstatus.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_status_pegawai(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
        
        if pegawai_db.objects.filter(status_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki status ini'
        else:        
            nstatus = status_pegawai_db.objects.get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus status pegawai : {nstatus.status}'
            )
            thapus.save()
            
            nstatus.delete()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


# Divisi
# ++++++++++++++
@login_required
def divisi(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Divisi'     
        }
        
        return render(request,'hrd_app/pengaturan/divisi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def divisi_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in divisi_db.objects.all().order_by('divisi'):
            
            div = {
                'id':i.id,
                'divisi':i.divisi,
            }
            data.append(div)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_divisi(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        ddiv = request.POST.get('divisi')
        
        if divisi_db.objects.filter(divisi = ddiv).exists():
            status = 'duplikat'
        else:    
            tdiv = divisi_db(
                divisi = ddiv,
            )
            tdiv.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_divisi(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        ddiv = request.POST.get('edivisi')
        
        if divisi_db.objects.filter(divisi = ddiv).exists():
            status = 'duplikat'
        else:    
            ndiv = divisi_db.objects.get(id=int(eid))
            ndiv.divisi = ddiv
            ndiv.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_divisi(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
        
        if pegawai_db.objects.filter(divisi_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki divisi ini'
        else:        
            ndiv = divisi_db.objects.get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus divisi : {ndiv.divisi}'
            )
            thapus.save()
            
            ndiv.delete()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


# Counter
# ++++++++++++++
@login_required
def counter(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Counter'     
        }
        
        return render(request,'hrd_app/pengaturan/counter.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def counter_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in counter_db.objects.all().order_by('counter'):
            
            ct = {
                'id':i.id,
                'counter':i.counter,
            }
            data.append(ct)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_counter(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dcounter = request.POST.get('counter')
        
        if counter_db.objects.filter(counter = dcounter).exists():
            status = 'duplikat'
        else:    
            tc = counter_db(
                counter = dcounter,
            )
            tc.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_counter(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        dcounter = request.POST.get('ecounter')
        
        if counter_db.objects.filter(counter = dcounter).exists():
            status = 'duplikat'
        else:    
            nct = counter_db.objects.get(id=int(eid))
            nct.counter = dcounter
            nct.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_counter(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
        
        if pegawai_db.objects.filter(counter_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki counter ini'
        else:        
            nct = counter_db.objects.get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus counter : {nct.counter}'
            )
            thapus.save()
            
            nct.delete()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


# Libur Nasional
# ++++++++++++++
@login_required
def libur_nasional(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Libur Nasional'     
        }
        
        return render(request,'hrd_app/pengaturan/libur_nasional.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def libur_nasional_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in libur_nasional_db.objects.all().order_by('tgl_libur'):
            
            tgl = i.tgl_libur.strftime('%d-%m-%Y')
            insentif = "{:,.0f}".format(i.insentif_karyawan)
            
            ln = {
                'id': i.id,
                'libur': i.libur,
                'tgl': tgl,
                'insentif': insentif.replace(',', '.')
            }
            data.append(ln)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_libur_nasional(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dtgl = request.POST.get('tgl')
        libur = request.POST.get('libur')
        dinsentif = request.POST.get('insentif')
        
        tgl = datetime.strptime(dtgl, '%d-%m-%Y').date()
        insentif = dinsentif.replace('.', '')
        
        if libur_nasional_db.objects.filter(tgl_libur = tgl).exists():
            status = 'duplikat'
        else:    
            ln = libur_nasional_db(
                tgl_libur = tgl,
                libur = libur,
                insentif_karyawan = insentif,
            )
            ln.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_libur_nasional(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        dtgl = request.POST.get('etgl')
        libur = request.POST.get('elibur')
        dinsentif = request.POST.get('einsentif')
        
        tgl = datetime.strptime(dtgl, '%d-%m-%Y').date()
        insentif = dinsentif.replace('.', '')
        
        if libur_nasional_db.objects.filter(tgl_libur = tgl, libur = libur, insentif_karyawan = insentif).exists():
            status = 'duplikat'
        else:    
            ln = libur_nasional_db.objects.get(id=int(eid))
            ln.tgl_libur = tgl
            ln.libur = libur
            ln.insentif_karyawan = insentif
            ln.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_libur_nasional(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
              
        ln = libur_nasional_db.objects.get(id=int(hid))            
        
        thapus = histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus libur nasional : {ln.libur}'
        )
        thapus.save()
        
        ln.delete()
        
        status = 'ok'
        
        return JsonResponse({"status": status})


# Jam Kerja
# ++++++++++++++
@login_required
def jam_kerja(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        kk = kelompok_kerja_db.objects.all().order_by('kelompok')
        
        data = {       
            'dsid': dsid,
            'kk': kk,
            'modul_aktif' : 'Jam Kerja'     
        }
        
        return render(request,'hrd_app/pengaturan/jam_kerja.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def tambah_kk_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        tkk = request.POST.get('tkk')
        
        data = []
                
        if kelompok_kerja_db.objects.filter(kelompok=tkk).exists():
            data = {}
            status = 'duplikat'
        else:
            tk = kelompok_kerja_db(
                kelompok = tkk
            )    
            tk.save()
            
            dkk = kelompok_kerja_db.objects.last()
        
            data = {
                'id': dkk.id,
                'text': dkk.kelompok
            }
            
            status = 'ok'         
                                
        return JsonResponse({"status": status, "data":data})


@login_required
# def jam_kerja_json(request):
        
#     if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
#         data = []
                
#         for i in jamkerja_db.objects.all().order_by('kk_id__kelompok'):            
            
#             jk = {
#                 'id': i.id,
#                 'kk': i.kk,
#                 'masuk': masuk,
#                 'ist': ist,
#                 'k_ist': k_ist,
#                 'ist2': ist2,
#                 'k_ist2': k_ist2,
#                 'pulang': pulang,
#             }
#             data.append(jk)
                                
#         return JsonResponse({"data": data})


@login_required
def tambah_jam_kerja(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dtgl = request.POST.get('tgl')
        libur = request.POST.get('libur')
        dinsentif = request.POST.get('insentif')
        
        tgl = datetime.strptime(dtgl, '%d-%m-%Y').date()
        insentif = dinsentif.replace('.', '')
        
        if libur_nasional_db.objects.filter(tgl_libur = tgl).exists():
            status = 'duplikat'
        else:    
            ln = libur_nasional_db(
                tgl_libur = tgl,
                libur = libur,
                insentif_karyawan = insentif,
            )
            ln.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_jam_kerja(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        dtgl = request.POST.get('etgl')
        libur = request.POST.get('elibur')
        dinsentif = request.POST.get('einsentif')
        
        tgl = datetime.strptime(dtgl, '%d-%m-%Y').date()
        insentif = dinsentif.replace('.', '')
        
        if libur_nasional_db.objects.filter(tgl_libur = tgl, libur = libur, insentif_karyawan = insentif).exists():
            status = 'duplikat'
        else:    
            ln = libur_nasional_db.objects.get(id=int(eid))
            ln.tgl_libur = tgl
            ln.libur = libur
            ln.insentif_karyawan = insentif
            ln.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_jam_kerja(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
              
        ln = libur_nasional_db.objects.get(id=int(hid))            
        
        thapus = histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus libur nasional : {ln.libur}'
        )
        thapus.save()
        
        ln.delete()
        
        status = 'ok'
        
        return JsonResponse({"status": status})


# Jenis Ijin
# ++++++++++++++
@login_required
def jenis_ijin(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Jenis Ijin'     
        }
        
        return render(request,'hrd_app/pengaturan/jenis_ijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def status_pegawai_lembur(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Status Pegawai Lembur'     
        }
        
        return render(request,'hrd_app/pengaturan/status_pegawai_lembur.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

    