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
import math
import json
import time
import pandas as pd
from decimal import *

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
        print(dsid)
        
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
        
        return render(request,'hrd_app/pegawai/pegawai/[sid]/pegawai.html', data)
        
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
        
        return render(request,'hrd_app/pegawai/non_aktif/[sid]/non_aktif.html', data)
        
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
                "tgl_lahir":k.tgl_lahir.strftime("%d-%m-%Y"),
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
                "kota":pd.kota_id,
                "nama_koka":pd.kota.nama_koka,
                "dari_tahun":pd.dari_tahun.strftime("%d-%m-%Y"),
                "sampai_tahun":pd.sampai_tahun.strftime("%d-%m-%Y"),
                "jurusan":pd.jurusan,
                "gelar":pd.gelar
            }
            pdk.append(obj)

        for pn in pengalaman:
            print(pn.kota_id)
            obj = {
                "perusahaan":pn.perusahaan,
                "kota":pn.kota_id,
                "nama_koka":pn.kota.nama_koka,
                "dari_tahun":pn.dari_tahun.strftime("%d-%m-%Y"),
                "sampai_tahun":pn.sampai_tahun.strftime("%d-%m-%Y"),
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
        pg.tgl_masuk = pg.tgl_masuk.strftime("%d-%m-%Y")
        data = serialize("json",kota_kabupaten)
        pribadi.tgl_lahir = pribadi.tgl_lahir.strftime("%d-%m-%Y")
        pribadi.tinggi_badan = ".".join(str(pribadi.tinggi_badan).split(","))
        pribadi.berat_badan = ".".join(str(pribadi.berat_badan).split(","))
        data = {
            'akses' : akses,
            'id':idp,
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
            'kota_kabupaten':kota_kabupaten,
            'modul_aktif' : 'Pegawai',
            'payroll':["Lainnya","HRD","Owner"],
            'goldarah':['O','A','B','AB'],
            'agama':['Islam','Katholik','Kristen','Hindu','Buddha','Konghucu'] 
        }
        print(data["pengalaman"])
        
        return render(request,'hrd_app/pegawai/epegawai/[sid]/edit.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@login_required
def epegawai(r,idp):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        user = akses_db.objects.get(pk=r.user.id)
        sid = user.sid_id
        nama = r.POST.get("nama")
        id = r.POST.get("id")
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
        pengalaman = r.POST.get("pengalaman")
        pendidikan = r.POST.get("pendidikan")
        keluarga = json.loads(keluarga)
        pihak = json.loads(pihak)
        pengalaman = json.loads(pengalaman)
        pendidikan = json.loads(pendidikan)
        status_pegawai = status_pegawai_db.objects.get(status="Staff")

        if pegawai_db.objects.filter(~Q(pk=int(idp)),userid=userid).exists():
            status = "duplikat"
        else:
            pegawai = pegawai_db.objects.filter(userid=userid).update(
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
                tgl_masuk=tgl_masuk,
                tgl_aktif=datetime.now().strftime('%Y-%m-%d'),
                hari_off_id=hr,
                kelompok_kerja_id=kk,
                sisa_cuti=12,
                counter_id=counter,
                add_by=r.user.username,
                edit_by=r.user.username

                # status
            )            

            

            # Pengalaman
            pengalaman_db.objects.filter(pegawai__userid=int(userid)).delete()
            for pgl in pengalaman:
                print(pgl)
                pengalaman_db(
                    pegawai_id=int(idp),
                    perusahaan=pgl['perusahaan'],
                    kota_id=pgl['kota'],
                    dari_tahun=datetime.strptime(pgl['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pgl['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jabatan=pgl['jabatan']
                ).save()


            # Pendidikan
            pendidikan_db.objects.filter(pegawai__userid=int(userid)).delete()
            for pdk in pendidikan:
                pendidikan_db(
                    pegawai_id=int(idp),
                    pendidikan=pdk['pendidikan'],
                    nama=pdk['nama'],
                    kota_id=pdk['kota'],
                    dari_tahun=datetime.strptime(pdk['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pdk['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jurusan=pdk['jurusan'],
                    gelar=pdk['gelar']
                ).save()


            # Tambah Pihak Lain
            pgw = pegawai_db.objects.get(userid=userid)
            kontak_lain_db.objects.filter(pegawai__userid=int(userid)).delete()
            for p in pihak:
                kontak_lain_db(
                pegawai_id=int(pgw.pk),
                hubungan = p['hubungan'],
                nama = p['nama'],
                gender = p['gender'],
                phone = p['phone']
                ).save()
            

            # Tambah Keluarga
            keluarga_db.objects.filter(pegawai__userid=int(userid)).delete()
            for k in keluarga:
                print(k)
                keluarga_db(
                    pegawai_id=int(pgw.pk),
                    hubungan = k['hubungan'],
                    nama = k["nama"],
                    tgl_lahir = datetime.strptime(k['tgl_lahir'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    gender = k['gender'],
                    gol_darah = k['gol_darah']
                ).save()

            # Tambah Data Pribadi
            pribadi = pribadi_db.objects.get(pegawai_id=id)
            if not pribadi:
                return False
            else:
                print(tinggi)
                pribadi_db.objects.filter(pegawai_id=id).update(
                    pegawai_id=int(pgw.pk),
                    alamat=alamat,
                    phone=phone,
                    email=email,
                    kota_lahir=kota_lahir,
                    tgl_lahir=tgl_lahir,
                    tinggi_badan=tinggi,
                    berat_badan=berat,
                    gol_darah=goldarah,
                    agama=agama
                )
            status= 'OK'
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)

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

        kota_kabupaten = kota_kabupaten_db.objects.all()
        
        data = {
            'akses' : akses,
            'dsid': dsid,
            "counter":counter,
            "divisi":divisi,
            "jabatan":jabatan,
            "kota_kabupaten":kota_kabupaten,
            "kk":kk,
            "hr":hr
        }
    return render(r,"hrd_app/pegawai/tpegawai/tambah.html",data)

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
        pengalaman = r.POST.get("pengalaman")
        pendidikan = r.POST.get("pendidikan")
        if keluarga:
            keluarga = json.loads(keluarga)
        else:
            keluarga = []
        

        if pihak:
            pihak = json.loads(pihak)
        else:
            pihak = []


        if pengalaman:
            pengalaman = json.loads(pengalaman)
        else:
            pengalaman = []
        

        if pendidikan:
            pendidikan = json.loads(pendidikan)
        else:
            pendidikan = []
        status_pegawai = status_pegawai_db.objects.get(status="Staff")

        if pegawai_db.objects.filter(userid=userid).exists():
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
            for pgl in pengalaman:
                pengalaman_db(
                    pegawai_id=int(pgw.pk),
                    perusahaan=pgl['perusahaan'],
                    kota_id=pgl['kota'],
                    dari_tahun=datetime.strptime(pgl['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pgl['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jabatan=pgl['jabatan']
                ).save()
            
            for pdk in pendidikan:
                pendidikan_db(
                    pegawai_id=int(pgw.pk),
                    pendidikan=pdk['pendidikan'],
                    nama=pdk['nama'],
                    kota_id=pdk['kota'],
                    dari_tahun=datetime.strptime(pdk['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pdk['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jurusan=pdk['jurusan'],
                    gelar=pdk['gelar']
                ).save()
            pribadi.save()
            status = "ok"
            print(sid)
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)


@login_required
def getPegawai(r,idp):
    result = serialize("json",[pegawai_db.objects.get(pk=int(idp))])
    result = json.loads(result)
    print(result[0])
    return JsonResponse({"data":result[0]},status=200,safe=False)


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
        pribadi = pribadi_db.objects.get(pegawai_id=pg.pk)
        kontak_lain = kontak_lain_db.objects.filter(pegawai_id=pg.pk)
        keluarga = keluarga_db.objects.filter(pegawai_id=pg.pk)
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            "pribadi":pribadi,
            "keluarga":keluarga,
            "kontak_lain":kontak_lain,
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
        pendidikan = pendidikan_db.objects.filter(pegawai_id=pg.pk)
        pdk = []
        for p in pendidikan:
            obj = p
            obj.kota = p.kota
            pdk.append(obj)
        print(pendidikan[0].dari_tahun)
        pengalaman = pengalaman_db.objects.filter(pegawai_id=pg.pk)
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'pengalaman':pengalaman,
            'pendidikan':pendidikan,
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
        
        pg =pegawai_db.objects.select_related("jabatan").get(id=int(idp))
        sid = pg.status_id          
        jabatan = jabatan_db.objects.all()
        print(jabatan)
        print(pg.jabatan_id)
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'jabatan_sebelum':pg.jabatan_id,
            'jabatan':jabatan,
            'pegawai':pegawai,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/promosi_demosi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')



@login_required
def tambah_prodemo(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        res = {"status":""}
        tgl = datetime.strptime(r.POST.get("tgl"),"%d-%m-%Y").strftime("%Y-%m-%d")
        status = r.POST.get("status")
        jabatan_seb = r.POST.get("jabatan_seb")
        jabatan_sek = r.POST.get("jabatan_sek")
        print(r.POST)
        idp = r.POST.get("id")

        if jabatan_seb ==  jabatan_sek:
            res["status"] = "Jabatan sama"
            return JsonResponse(res,status=400,safe=False)
        
        
        if status == "0":
            status = "Demosi"
        else:
            status = "Promosi"
        
        pgw = pegawai_db.objects.get(pk=int(idp))
        if not pgw:
            res['status'] = 'Pegawai tidak ada'
            return JsonResponse(res,status=400,safe=False)
        

        promosi_demosi_db(tgl=tgl,pegawai_id=int(idp),status=status,jabatan_sebelum_id=int(pgw.jabatan_id),jabatan_sekarang_id=int(jabatan_sek)).save()
        pg = pegawai_db.objects.get(pk=int(idp))
        pg.jabatan_id=int(jabatan_sek)
        pg.save()
        res["status"] = "Success"
        return JsonResponse(res,status=201,safe=False)

        

def promodemo_json(r,idp):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        status = r.POST.get("status")
        print(r.POST)
        if status == "0":
            result = promosi_demosi_db.objects.filter(pegawai_id=int(idp),status="demosi")
        else:
            result = promosi_demosi_db.objects.filter(pegawai_id=int(idp),status="promosi")
        
        rslt = []
        for r in result:
            obj = {
                "tgl":r.tgl,
                "jabatan_sebelum":r.jabatan_sebelum.jabatan,
                "jabatan_sekarang":r.jabatan_sekarang.jabatan
            }

            rslt.append(obj)
        return JsonResponse({'data':rslt},status=200,safe=False)


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
def get_sangsi_pegawai(r,idp):
    sangsi = sangsi_db.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now()).last()
    if not sangsi:
        sangsi = {}
    else:
        sangsi = serialize("json",[sangsi])
        sangsi = json.loads(sangsi)[0]
    return JsonResponse({"data":sangsi},status=200,safe=False)

@login_required
def sangsi_json(r,idp):
    sangsi = sangsi_db.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now())
    result = []
    for s in sangsi:
        obj = {
            "tgl_berlaku":s.tgl_berlaku,
            "tgl_berakhir":s.tgl_berakhir,
            "status":s.status_sangsi,
            "deskripsi":s.deskripsi_pelanggaran
        }
        result.append(obj)
    return JsonResponse({"data":result})

@login_required
def tambah_sangsi(r,idp):

    # cek dari xmlhttprequest
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        tgl_berlaku = r.POST.get("tgl_berlaku")
        tgl_berakhir = r.POST.get("tgl_berakhir")
        status = r.POST.get("status")
        deskripsi = r.POST.get("deskripsi")

        # if status != "SP1" or status != "SP2" or status != "SP3":
        #      return JsonResponse({"status":"XIXIIX"},safe=False,status=400)
        # cek jika sp tersebut masih ada
        if sangsi_db.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now(),status_sangsi="SP3").exists():
            return JsonResponse({"status":"Kudunya dipecat ga si!"},safe=False,status=400)
        print(tgl_berakhir)
        if sangsi_db.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now(),status_sangsi=status).exists():
            return JsonResponse({"status":"Sangsi "+ status+" Sudah ada!"},safe=False,status=400)

    
        sangsi_db(
            pegawai_id=int(idp),
            tgl_berlaku=tgl_berlaku,
            tgl_berakhir=tgl_berakhir,
            status_sangsi=status,
            deskripsi_pelanggaran=deskripsi
        ).save()
        return JsonResponse({'status':"success create sangsi"},status=201,safe=False)


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
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
                
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur,
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            'sid': int(sid),
            'sil': sid_lembur,
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            'sid': int(sid),
            'dari':dari,
            'sampai':sampai,
            'sil': sid_lembur,
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
        tminus1 = date.today() + timedelta(days=-1)
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
            if int(sid) == int(p.status_id): 
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
                    "status":p.status.status,
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
    for m in mesin_db.objects.filter(status='Active'):
        
        ip = m.ipaddress
        conn = None
        zk = ZK(ip, port=4370, timeout=65)
        try:
            conn = zk.connect()
            conn.disable_device()

            # Data absensi
            absensi = conn.get_attendance()
            for a in absensi:
                print(luserid)
                if dari <= a.timestamp <= sampai:   
                    if a.user_id in luserid:              
                        data = {
                            "userid": a.user_id,
                            "jam_absen": datetime.strftime(a.timestamp,"%Y-%m-%d %H:%M:%S"),
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
    # dmesin.append({
    #     "userid":"107319",
    #     "jam_absen":"2024-07-18 08:02:43",
    #     "punch":0,
    #     "mesin":"FS"
    # })
    with open(r"static/data.json","r") as f:
        att = f.read()
    att = json.loads(att)
    att = sorted(att, key=lambda i: i['jam_absen'])
    print(att)

    # att = sorted(att, key=lambda i: i['jam_absen'])
    ddr = []
    # jika istirahat sama maka jan masukin ke b INGETTTT
    
        
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
                
                jam_absen = datetime.strptime(a['jam_absen'],"%Y-%m-%d %H:%M:%S")
                pg = next((pgw for pgw in pegawai if pgw["userid"] == a["userid"]),None)
                # # Versi Cirebon

                for r in rangetgl:
                    tmin = r + timedelta(days=-1)
                    tplus = r + timedelta(days=1)
                    ab = absensi_db.objects.select_related('pegawai').get(tgl_absen=r.date(), pegawai__userid=a['userid'])
                    if jam_absen.date() == r.date():
                        bb_msk = jam_absen - timedelta(hours=5)
                        ba_msk = jam_absen + timedelta(hours=5)
                        jk = None
                        if a["punch"] == 0:
                            jk = jamkerja_db.objects.filter(kk_id=ab.pegawai.kelompok_kerja.pk,jam_masuk__gte=bb_msk.time(),jam_masuk__lte=ba_msk.time()).order_by("-jam_masuk")
                        elif a["punch"] == 1:
                            jk = jamkerja_db.objects.filter(kk_id=ab.pegawai.kelompok_kerja.pk,jam_pulang__gte=bb_msk.time(),jam_pulang__lte=ba_msk.time()).order_by("-jam_pulang")

                        if jk is not None and ab.jam_masuk is None and ab.jam_pulang is None:
                            selisih = []
                            mins = 0.0
                            for j in jk:
                                if j.jam_masuk < jam_absen.time():
                                    s = jam_absen - datetime.combine(jam_absen.date(),j.jam_masuk)
                                    selisih.append(s.total_seconds() / 60)
                                else:
                                    s = datetime.combine(jam_absen.date(),j.jam_masuk) - jam_absen
                                    selisih.append(s.total_seconds() / 60)
                            if len(selisih) > 0:
                                mins = selisih[0]
                                for s in selisih:
                                    if s < mins:
                                        mins = s
                            if mins != 0:
                                jk = jk[selisih.index(mins)]
                                time = datetime.combine(jam_absen.date(),jk.jam_kembali_istirahat) - datetime.combine(jam_absen.date(),jk.jam_istirahat)
                                time2 = datetime.combine(jam_absen.date(),jk.jam_kembali_istirahat2) - datetime.combine(jam_absen.date(),jk.jam_istirahat2)
                                ist = [str(jam_absen.date())+" " + str(time),str(jam_absen.date())+" " + str(time2)]
                                ist_format = datetime.strptime(ist[0],"%Y-%m-%d %H:%M:%S")
                                ist2_format = datetime.strptime(ist[1],"%Y-%m-%d %H:%M:%S")
                                ist_t = ist_format.hour + ist_format.minute / 60 + ist_format.second / 3600
                                ist_t2 = ist2_format.hour + ist2_format.minute / 60 + ist2_format.second / 3600


                                ab.jam_masuk = jk.jam_masuk
                                ab.jam_pulang = jk.jam_pulang
                                ab.lama_istirahat = ist_t
                                ab.lama_istirahat2 = ist_t2
                                ab.jam_istirahat = ist_t
# ++++++++++++++++++++++++++++++++++++++++  MASUK  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        if a["punch"] == 0 and jam_absen.hour > 4 and jam_absen.hour < 18 :
                            if ab.masuk is not None:
                                if (int(jam_absen.hour) - int(ab.masuk.hour)) > 7:
                                    ab.masuk_b = jam_absen.time()
                                    ab.save()
                                else:
                                    ab.masuk = jam_absen.time()
                                    ab.save()
                            elif ab.pulang is not None or ab.istirahat is not None or ab.kembali is not None:
                                if ab.masuk is None:
                                    ab.masuk = jam_absen.time()
                                    ab.save()
                                else:
                                    ab.masuk_b = jam_absen.time()
                                    ab.save()
                            else:
                                ab.masuk = jam_absen.time()
                                ab.save()
# ++++++++++++++++++++++++++++++++++++++++  MASUK MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 0 and jam_absen.hour > 18:
                            # pastikan untuk userid hotel
                            if pg["status_id"] == 3:
                                if ab.masuk is not None or ab.istirahat is not None or ab.kembali is not None or ab.pulang is not None:
                                    try:
                                        ab2 = absensi_db.objects.get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
                                        if ab2.masuk is None:
                                            ab2.masuk = jam_absen.time()
                                            ab2.save()
                                        else:
                                            if int(ab2.masuk.hour) > 18:
                                                pass
                                            else:
                                                ab2.masuk = jam_absen.time()
                                                ab2.save()
                                    except:
                                        absensi_db(
                                            tgl_absen=tplus.date(),
                                            pegawai_id=ab.pegawai_id,
                                            masuk=jam_absen.time()
                                        ).save()                    
                                else:
                                    ab.masuk = jam_absen.time()
                                    ab.save()
                            else:
                                if ab.masuk is not None:
                                    if int(ab.masuk.hour) < 18:
                                        ab.masuk_b = jam_absen.time()
                                        ab.save()
                                    else:
                                        pass
                                elif ab.pulang is not None or ab.istirahat is not None or ab.kembali is not None:
                                    ab.masuk_b = jam_absen.time()
                                    ab.save()
                                else:
                                    ab.masuk = jam_absen.time()
                                    ab.save()
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 2 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                            if ab.istirahat is not None:
                                if (int(jam_absen.hour) - int(ab.istirahat.hour)) > 4:
                                    ab.istirahat_b = jam_absen.time()
                                    ab.save()
                                else:
                                    pass
                            elif ab.pulang is not None or ab.kembali is not None or ab.masuk_b is not None or ab.masuk is not None:
                                if ab.istirahat is not None:
                                    ab.istirahat_b = jam_absen.time()
                                    ab.save()
                                else:
                                    ab.istirahat = jam_absen.time()
                                    ab.save()
                            else:
                                ab.istirahat = jam_absen.time()
                                ab.save()
                                        
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 2 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
                            if int(jam_absen.hour) > 21:
                                if ab.masuk_b is not None:
                                    if int(ab.masuk_b.hour) > 18:
                                        ab.istirahat_b = jam_absen.time()
                                        ab.save()
                                    else:
                                        pass
                                else:
                                    if ab.pulang_b is not None:
                                       pass
                                    else:
                                        ab.istirahat_b = jam_absen.time()
                                        ab.save()
                                       

                            elif int(jam_absen.hour) < 8:
                                if pg is not None:
                                    if pg["status_id"] == 3:
                                        if ab.masuk is not None:
                                            if int(ab.masuk.hour) > 18:
                                                ab.istirahat = jam_absen.time()
                                                ab.save()
                                            else:
                                                pass
                                        else:
                                            try:
                                                ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                                if ab2.masuk is not None:
                                                    if ab2.masuk.hour > 18:
                                                        ab2.istirahat = jam_absen.time()
                                                        ab2.save()
                                                    else:
                                                        ab.istirahat = jam_absen.time()
                                                        ab.save()
                                                elif ab2.kembali is not None:
                                                    if ab2.kembali.hour > 9:
                                                        ab.istirahat = jam_absen.time()
                                                        ab.save()
                                                    else:
                                                        ab2.istirahat = jam_absen.time()
                                                        ab2.save()
                                                elif ab2.pulang is not None:
                                                    if ab2.pulang.hour > 9:
                                                        ab.istirahat = jam_absen.time()
                                                        ab.save()
                                                    else:
                                                        ab2.istirahat = jam_absen.time()
                                                        ab2.save()
                                                else:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                            except absensi_db.DoesNotExist:
                                                ab.istirahat = jam_absen.time()
                                                ab.save()
                                    else:
                                        try:
                                            # tanda
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.masuk is not None or ab2.kembali is not None:
                                                ab2.istirahat_b = jam_absen.time()
                                                ab2.save()
                                            elif ab2.istirahat is not None:
                                                if int(ab2.istirahat.hour) < 8 or int(ab2.istirahat.hour) > 21:
                                                    pass
                                                else:
                                                    ab2.istirahat_b = jam_absen.time()
                                                    ab2.save()
                                            elif ab2.pulang is not None:
                                                ab2.istirahat_b = jam_absen.time()
                                                ab2.save()
                                            else:
                                                if ab2.masuk_b is not None:
                                                    if int(ab2.masuk_b.hour) > 18:
                                                        ab2.istirahat_b = jam_absen.time()
                                                        ab2.save()
                                                    else:
                                                        pass
                                                else:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                        except absensi_db.DoesNotExist:
                                            ab.istirahat = jam_absen.time()
                                            ab.save()
                                else:
                                    pass
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 4 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                            if ab.istirahat2 is not None:
                                if (int(jam_absen.hour) - int(ab.istirahat2.hour)) > 4:
                                    ab.istirahat2_b = jam_absen.time()
                                    ab.save()
                                else:
                                    pass
                            elif ab.pulang is not None or ab.kembali2 is not None or ab.masuk_b is not None:
                                ab.istirahat2_b = jam_absen.time()
                                ab.save()
                            else:
                                ab.istirahat2 = jam_absen.time()
                                ab.save()
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 4 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
                            if pg is not None:
                                if pg["status_id"] == 3:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
                                            ab.istirahat2 = jam_absen.time()
                                            ab.save()
                                        else:
                                            pass
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
                                                    ab.istirahat2 = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    ab2.istirahat2 = jam_absen.time()
                                                    ab2.save()
                                            elif ab2.istirahat is not None:
                                                if int(ab2.istirahat.hour) > 8 and int(ab2.istirahat.hour) < 21:
                                                    ab.istirahat2 = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    ab2.istirahat2 = jam_absen.time()
                                                    ab2.save()
                                            elif ab2.kembali is not None:
                                                if int(ab2.kembali.hour) > 8 and int(ab2.kembali.hour) < 21:
                                                    ab.istirahat2 = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    ab2.istirahat2 = jam_absen.time()
                                                    ab2.save()
                                            elif ab2.pulang is not None:
                                                pass
                                            else:
                                                ab2.istirahat2 = jam_absen.time()
                                                ab2.save()
                                        except absensi_db.DoesNotExist:
                                            absensi_db(
                                                tgl_absen=tmin.date(),
                                                pegawai_id=ab.pegawai.pk,
                                                istirahat2=jam_absen.time()
                                            ).save()
                                else:
                                    try:
                                        ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.masuk is not None:
                                            if int(ab2.masuk.hour) > 18:
                                                ab2.istirahat2 = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.istirahat2_b = jam_absen
                                                ab2.save()
                                        elif ab2.istirahat is not None:
                                            if int(ab2.istirahat.hour) < 8 or int(ab2.istirahat.hour) > 21:
                                                pass
                                            else:
                                                ab2.istirahat2_b = jam_absen
                                                ab2.save()
                                        elif ab2.kembali is not None:
                                            if int(ab2.kembali.hour) < 8 or int(ab2.kembali.hour) > 21:
                                                ab2.istirahat2 = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.istirahat2_b = jam_absen
                                                ab2.save()
                                        elif ab2.pulang is not None:
                                            if int(ab2.pulang.hour) < 9:
                                                ab2.istirahat2 = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.istirahat2_b = jam_absen
                                                ab2.save()
                                        else:
                                            if ab2.masuk_b is not None:
                                                if int(ab2.masuk_b.hour) > 18:
                                                    ab2.istirahat2_b = jam_absen
                                                    ab2.save()
                                                else:
                                                    pass
                                            else:
                                                ab2.istirahat2_b = jam_absen
                                                ab2.save()
                                    except absensi_db.DoesNotExist:
                                        absensi_db(
                                            tgl_absen=tmin.date(),
                                            pegawai_id=ab.pegawai.pk,
                                            istirahat2=jam_absen
                                        ).save()
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 3 and int(jam_absen.hour) > 9:
                            if ab.kembali is not None:
                                if int(jam_absen.hour) - int(ab.kembali.hour) > 4:
                                    ab.kembali_b = jam_absen.time()
                                    ab.save()
                                else:
                                    pass
                            elif ab.masuk_b is not None or ab.pulang is not None or ab.istirahat_b is not None:
                                ab.kembali_b = jam_absen.time()
                                ab.save()
                            else:
                                ab.kembali = jam_absen.time()
                                ab.save()
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 5 and int(jam_absen.hour) > 9:
                            if ab.kembali2 is not None:
                                if int(jam_absen.hour) - int(ab.kembali2.hour) > 4:
                                    ab.kembali2_b = jam_absen.time()
                                    ab.save()
                                else:
                                    pass
                            elif ab.masuk_b is not None or ab.pulang is not None or ab.istirahat2_b is not None:
                                ab.kembali2_b = jam_absen.time()
                                ab.save()
                            else:
                                ab.kembali2 = jam_absen.time()
                                ab.save()
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 5 and int(jam_absen.hour) < 9:
                            if pg is not None:
                                if pg["status_id"] == 3:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
                                            ab.kembali2 = jam_absen.time()
                                            ab.save()
                                        else:
                                            pass
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
                                                    ab.kembali2 = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save()
                                            elif ab2.istirahat is not None:
                                                if int(ab2.istirahat.hour) > 8 and int(ab2.istirahat.hour) < 21:
                                                    ab.kembali2 = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save()
                                            elif ab2.kembali is not None:
                                                if int(ab2.kembali.hour) > 8 and int(ab2.kembali.hour) < 21:
                                                    ab.kembali2 = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save()
                                            elif ab2.pulang is not None:
                                                # if int(ab2.pulang.hour) > 9:
                                                # ab.kembali2 = jam_absen.time()
                                                # ab.save()
                                                pass
                                                # else:
                                                #     ab2.kembali2 = jam_absen.time()
                                                #     ab2.save()
                                            else:
                                                ab2.kembali2 = jam_absen.time()
                                                ab2.save()
                                        except absensi_db.DoesNotExist:
                                            ab.kembali  = jam_absen.time()
                                            ab.save()
                                else:
                                    try:
                                        ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.masuk is not None:
                                            if int(ab2.masuk.hour) > 18:
                                                ab2.kembali2 = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.kembali2_b = jam_absen
                                                ab2.save()
                                        elif ab2.istirahat is not None:
                                            if int(ab2.istirahat.hour) < 8 or int(ab2.istirahat.hour) > 21:
                                                ab2.kembali2 = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.kembali2_b = jam_absen
                                                ab2.save()
                                        elif ab2.kembali is not None:
                                            if int(ab2.kembali.hour) < 8 or int(ab2.kembali.hour) > 21:
                                                pass
                                            else:
                                                ab2.kembali2_b = jam_absen
                                                ab2.save()
                                        elif ab2.pulang is not None:
                                            if int(ab2.pulang.hour) < 9:
                                                ab2.kembali2 = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.kembali2_b = jam_absen
                                                ab2.save()
                                        else:
                                            if ab2.masuk_b is not None:
                                                if int(ab2.masuk_b.hour) > 18:
                                                    ab2.kembali2_b = jam_absen.time()
                                                    ab2.save()
                                                else:
                                                    pass
                                            else:
                                                ab2.kembali2_b = jam_absen.time()
                                                ab2.save()
                                    except absensi_db.DoesNotExist:
                                        ab.kembali2 = jam_absen.time()
                                        ab.save()
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI MALAM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 3 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 9):
                            if int(jam_absen.hour) > 21:
                                if ab.masuk_b is not None:
                                    if int(ab.masuk_b.hour) > 18:
                                        ab.kembali_b = jam_absen
                                        ab.save()
                                    else:
                                        pass
                                else:
                                    if ab.pulang_b is not None:
                                        pass
                                    else:
                                        ab.kembali_b = jam_absen
                                        ab.save()
                            elif int(jam_absen.hour) < 9:
                                if pg is not None:
                                    if pg["status_id"] == 3:
                                        # hari esok
                                        if ab.masuk is not None:
                                            if int(ab.masuk.hour) > 18:
                                                ab.kembali = jam_absen.time()
                                                ab.save()
                                            else:
                                                pass
                                        else:
                                            try:
                                                ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                                if ab2.masuk is not None:
                                                    if int(ab2.masuk.hour) < 18:
                                                        ab.kembali = jam_absen.time()
                                                        ab.save()
                                                    else:
                                                        ab2.kembali = jam_absen.time()
                                                        ab2.save()
                                                elif ab2.istirahat is not None or ab2.kembali is not None or ab2.pulang is not None:
                                                    ab.kembali = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    ab2.kembali = jam_absen.time()
                                                    ab2.save()
                                            except absensi_db.DoesNotExist:
                                                ab.kembali = jam_absen.time()
                                                ab.save()
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.kembali is not None:
                                                if int(jam_absen.hour) - int(ab2.kembali.hour) > 5:
                                                    ab2.kembali_b = jam_absen
                                                    ab2.save()
                                                else:
                                                    pass
                                            elif ab2.pulang is not None:
                                                ab2.kembali_b = jam_absen
                                                ab2.save()
                                            else:
                                                if ab2.masuk_b is not None:
                                                    ab2.kembali_b = jam_absen.time()
                                                    ab2.save()
                                                else:
                                                    ab2.kembali = jam_absen.time()
                                                    ab2.save()
                                        except absensi_db.DoesNotExist:
                                            ab.kembali = jam_absen.time()
                                            ab.save()
                                else:
                                    pass
# ++++++++++++++++++++++++++++++++++++++++  PULANG  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 1 and int(jam_absen.hour) > 9:
                            if ab.pulang is None: 
                                if ab.istirahat_b is not None or ab.kembali_b is not None:
                                    ab.pulang_b = jam_absen.time()
                                    ab.save()
                                else:
                                    ab.pulang = jam_absen.time()
                                    ab.save()
                            else:
                                if (int(jam_absen.hour) - int(ab.pulang.hour)) > 5:
                                    ab.pulang_b = jam_absen.time()
                                    ab.save()
                                else:
                                    ab.pulang = jam_absen.time()
                                    ab.save()
# ++++++++++++++++++++++++++++++++++++++++  PULANG MALAM  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 1 and int(jam_absen.hour) < 9:
                            if pg is not None:
                                if pg["status_id"] == 3:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
                                            ab.pulang = jam_absen.time()
                                            ab.save()
                                        else:
                                            pass
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.pulang is not None:
                                                if int(ab2.pulang.hour) > 9:
                                                    ab.pulang = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    pass
                                            elif ab.istirahat is not None or ab.kembali is not None or ab.masuk is not None:
                                                ab.pulang = jam_absen.time()
                                                ab.save()
                                            elif ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
                                                    ab.pulang = jam_absen.time()
                                                    ab.save()
                                                else:
                                                    pass
                                            else:
                                                ab2.pulang = jam_absen.time()
                                                ab2.save()
                                        except absensi_db.DoesNotExist:
                                            ab.pulang = jam_absen.time()
                                            ab.save()
                                else:
                                    try:
                                        ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.masuk is not None:
                                            if int(ab2.masuk.hour) > 18:
                                                ab2.pulang = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save()
                                        elif ab2.istirahat is not None:
                                            if int(ab2.istirahat.hour) < 8 or int(ab2.istirahat.hour) > 21:
                                                ab2.pulang = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save()
                                        elif ab2.kembali is not None:
                                            if int(ab2.kembali.hour) < 8 or int(ab2.kembali.hour) > 21:
                                                pass
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save()
                                        elif ab2.pulang is not None:
                                            if int(ab2.pulang.hour) < 9:
                                                ab2.pulang = jam_absen
                                                ab2.save()
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save()
                                        else:
                                            if ab2.masuk_b is not None:
                                                if int(ab2.masuk_b.hour) > 18:
                                                    ab2.pulang_b = jam_absen.time()
                                                    ab2.save()
                                                else:
                                                    pass
                                            else:
                                                ab2.pulang_b = jam_absen.time()
                                                ab2.save()
                                    except absensi_db.DoesNotExist:
                                        ab.pulang = jam_absen.time()
                                        ab.save()


                            # if ab.masuk is not None:
                            #     if int(ab.masuk.hour) < 18:
                            #         ab.kembali = jam_absen.time()
                            #         ab.save()
                            #     else:
                            #         pass
                            # else:
                            #     if ab.pulang is not None:
                            #        pass
                            #     else:
                            #         ab.kembali = jam_absen.time()
                            #         ab.save()


                            
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
            "ijin" : i.ijin.jenis_ijin,
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
                # rencana cronjob jalan
                if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                    print("MASUKKKKK")
                    print(p["hari_off"],nh)
                    if p['hari_off'] == nh:
                        # jika dia bisa mendapatkan opg 
                        print("LUAR OPG")
                        if p['status_id'] in lsopg:
                            print("DALAM OPG")
                            # jika ada geder off dari hari ini ke hari lain
                            if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                pass
                            # jika tidak ada
                            else:
                                # jika sudah ada opg yang ditambahkan (rencana cronjob)
                                if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                    pass
                                # jika tidak
                                else:
                                    tambah_opg = opg_db(
                                        pegawai_id = ab.pegawai_id,
                                        opg_tgl = ab.tgl_absen,   
                                        keterangan = 'OFF Pengganti Reguler',                         
                                        add_by = 'Program',
                                    )    
                                    print("MSK")
                                    tambah_opg.save()
                        else:
                            pass
                    else:
                        pass
                    
                    # sama aja kaya sebelumnya
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
                            
                # jika ada masuk dan pulang   
                else:
                    # jika dinas luar
                    if ab.pegawai_id in dl_idp:
                        
                        # jika off dia hari ini
                        if p['hari_off'] == nh:
                            # jika dia bisa mendapatkan opg
                            if p['status_id'] in lsopg:
                                # jika dia geser dari hari off ke hari lain
                                if geseroff_db.objects.filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                    pass
                                # jika dia tidak geser dari hari off ke hari lain
                                else:
                                    # ini rencana jika cronjob jalan
                                    if opg_db.objects.filter(opg_tgl=ab.tgl_absen,pegawai_id=ab.pegawai_id,keterangan='OFF Pengganti Reguler').exists():
                                        pass
                                    else:
                                        # ini kalo tidak jalan
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
                            # jika on off
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
                        # jika dia hari ini off
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
                    # jika hari ini dia adalah off nya
                
                # libur nasional
                for l in libur:
                # jika ada absen di hari libur nasional
                    if l['tgl_libur'] == ab.tgl_absen:                            
                        ab.libur_nasional = l['libur']
                        ab.save()
                        
                        # Hari Minggu
                        if nh == 'Minggu':
                            if p['status_id'] in lsopg:
                                
                                # Staff
                                if p['status'] == 'Staff':
                                    # jika hari off nya adalah hari minggu dan masuk maka hanya akan mendapatkan 1 opg
                                    if p['hari_off'] == nh:
                                        if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
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
                                        if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
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
                                                    
                                                    # ditasik tidak ada insentif dihari minggu jika masuk
                                                    # ab.insentif = l['insentif_karyawan']
                                                    # ab.save()
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
                                        # JIKA DIA MASUK DIHARI MERAH DILIBUR REGULERNYA MAKA AKAN DAPAT 2 OPG
                                        if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
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
                                        # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
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
                                # JIKA MASUK HANYA MENDAPATKAN 1 OPG DAN INSENTIF
                                else:
                                    if p['hari_off'] == nh:
                                        if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
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
                    # jika didalam data cuti ada pegawai id
                    if a.pegawai_id == c['idp']:
                        # jika tgl cuti sama dengan tgl absen
                        if c['tgl_cuti'] == ab.tgl_absen:
                            # jika tidak masuk dan pulang
                            if (ab.masuk is None and ab.pulang is None) or (ab.masuk_b is None and ab.pulang_b is None):
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
                                # jika jam kerja kurang dari 4 jam
                                if int(selisih.hour) <= 4:
                                    ab.keterangan_absensi = c['keterangan']
                                    ab.save()
                                # jika jam kerja lebih dari 4 jam
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
                            # jika ada geser off dan dia tidak masuk
                            if ab.masuk is None and ab.pulang is None and ab.masuk_b is None and ab.pulang_b is None:
                                drt = datetime.strftime(g['dari_tgl'], '%d-%m-%Y')
                                ab.keterangan_absensi = f'Geser OFF-({drt})' 
                                ab.save()
                            # jika ada geser off dan dia masuk
                            else:
                                geseroff_db.objects.get(id=int(g['id'])).delete()    
                        else:
                            pass
                
                # opg
                for o in opg:
                    if a.pegawai_id == o['idp']:
                        # cek jika di dalam data opg diambil pada tanggal saat ini
                        if o['diambil_tgl'] == ab.tgl_absen:
                            
                            opg = opg_db.objects.get(id=o['id'])
                            # jika tidak masuk dan tidak ada pulang
                            if ab.masuk is None and ab.pulang is None and ab.masuk_b is None and ab.pulang_b is None:
                                topg = datetime.strftime(o['diambil_tgl'], '%d-%m-%Y')
                                ab.keterangan_absensi = f'OPG-({topg})'
                                ab.save()                                
                                
                                opg.status = 1
                                opg.edit_by ='Program'
                                opg.save()
                            # jika masuk dan pulang
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
                        
                        tplus = ab.tgl_absen        
                        
                        dmsk = f'{ab.tgl_absen} {ab.masuk}'
                        dplg = f'{tplus} {ab.pulang}'
                        
                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih = plg - msk
                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                        # Split the string to separate the date and time parts
                        date_part, delta_part, time_part = djam_selisih.split(' ', 2)
                        # Parse the date and time
                        base_datetime = datetime.strptime(date_part + ' ' + time_part.split(",")[1], '%Y-%m-%d %H:%M:%S')

                        # Adjust the date based on the delta part
                        if delta_part == '-1':
                            adjusted_datetime = base_datetime - timedelta(days=1)
                        elif delta_part == '+1':
                            adjusted_datetime = base_datetime + timedelta(days=1)
                        else:
                            adjusted_datetime = base_datetime
                        selisih = adjusted_datetime
                        if int(selisih.hour) <= 4:
                            tjk = 0
                        else:
                            detik = selisih.second / 3600
                            menit = selisih.minute / 60
                            hour = selisih.hour
                            
                            jam = int(hour) + float(menit) + float(detik)
                            print(jam)
                            tjk = jam                
                else:
                    tjk = 0

                if ab.masuk_b is not None and ab.pulang_b is not None:
                    if ab.pulang_b > ab.masuk_b:
                        
                        dmsk_b = f'{ab.tgl_absen} {ab.masuk_b}'
                        dplg_b = f'{ab.tgl_absen} {ab.pulang_b}'
                        
                        msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
                        plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_b = plg_b - msk_b
                        djam_selisih_b = f'{ab.tgl_absen} {dselisih_b}'
                        selisih_b = datetime.strptime(djam_selisih_b, '%Y-%m-%d %H:%M:%S')
                        
                        if int(selisih_b.hour) <= 4:
                            tjk_b = 0
                        else:
                            detik_b = selisih_b.second / 3600
                            menit_b = selisih_b.minute / 60
                            hour_b = selisih_b.hour
                            
                            jam_b = int(hour_b) + float(menit_b) + float(detik_b)
                            
                            tjk_b = jam_b                   
                    else: 
                        
                        tplus_b = ab.tgl_absen
                        dmsk_b = f'{ab.tgl_absen} {ab.masuk_b}'
                        dplg_b = f'{tplus_b} {ab.pulang_b}'
                        
                        msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
                        plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
                        dselisih_b = plg_b - msk_b
                        # if dselisih_b.hour < 10:

                        djam_selisih_b = f'{ab.tgl_absen} {dselisih_b}'
                        print(djam_selisih_b)

                        # Split the string to separate the date and time parts
                        print(djam_selisih_b,"COBA")
                        date_part, delta_part, time_part = djam_selisih_b.split(' ', 2)
                        # Parse the date and time
                        base_datetime = datetime.strptime(date_part + ' ' + time_part.split(",")[1], '%Y-%m-%d %H:%M:%S')

                        # Adjust the date based on the delta part
                        if delta_part == '-1':
                            adjusted_datetime = base_datetime - timedelta(days=1)
                        elif delta_part == '+1':
                            adjusted_datetime = base_datetime + timedelta(days=1)
                        else:
                            adjusted_datetime = base_datetime
                        selisih_b = adjusted_datetime
                        print(selisih_b.hour,"SELISIH")
                        if int(selisih_b.hour) <= 4:
                            tjk_b = 0
                        else:
                            detik_b = selisih_b.second / 3600
                            menit_b = selisih_b.minute / 60
                            hour_b = selisih_b.hour
                            
                            jam_b = int(hour_b) + float(menit_b) + float(detik_b)
                            
                            tjk_b = jam_b                
                else:
                    tjk_b = 0
                    
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
                
                if ab.istirahat_b is not None and ab.kembali_b is not None:
                    if ab.kembali_b > ab.istirahat_b:
                        
                        dist_b = f'{ab.tgl_absen} {ab.istirahat_b}'
                        dkmb_b = f'{ab.tgl_absen} {ab.kembali_b}'
                        
                        ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
                        kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_i_b = kmb_b - ist_b
                        djam_selisih_i_b = f'{ab.tgl_absen} {dselisih_i_b}'
                        selisih_i_b = datetime.strptime(djam_selisih_i_b, '%Y-%m-%d %H:%M:%S')
                            
                        detik_i_b = selisih_i_b.second / 3600
                        menit_i_b = selisih_i_b.minute / 60
                        hour_i_b = selisih_i_b.hour
                        
                        jam_i_b = int(hour_i_b) + float(menit_i_b) + float(detik_i_b)
                        
                        tji_b = jam_i_b                   
                    else:
                        if int(ab.pegawai.status.id) == 3:
                            tplus_b = ab.tgl_absen + timedelta(days=1)
                        else:
                            tplus_b = ab.tgl_absen
                        dist_b = f'{ab.tgl_absen} {ab.istirahat_b}'
                        dkmb_b = f'{tplus_b} {ab.kembali_b}'
                        
                        ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
                        kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_i_b = kmb_b - ist_b
                        djam_selisih_i_b = f'{ab.tgl_absen} {dselisih_i_b}'
                        selisih_i_b = datetime.strptime(djam_selisih_i_b, '%Y-%m-%d %H:%M:%S')
                            
                        detik_i_b = selisih_i_b.second / 3600
                        menit_i_b = selisih_i_b.minute / 60
                        hour_i_b = selisih_i_b.hour
                        
                        jam_i_b = int(hour_i_b) + float(menit_i_b) + float(detik_i_b)
                        
                        tji_b = jam_i_b                      
                else:
                    tji_b = 0        
                
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

                if ab.istirahat2_b is not None and ab.kembali2_b is not None:
                    if ab.kembali2_b > ab.istirahat2_b:
                        
                        dist2_b = f'{ab.tgl_absen} {ab.istirahat2_b}'
                        dkmb2_b = f'{ab.tgl_absen} {ab.kembali2_b}'
                        
                        ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
                        kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_i2_b = kmb2_b - ist2_b
                        djam_selisih_i2_b = f'{ab.tgl_absen} {dselisih_i2_b}'
                        selisih_i2_b = datetime.strptime(djam_selisih_i2_b, '%Y-%m-%d %H:%M:%S')
                            
                        detik_i2_b = selisih_i2_b.second / 3600
                        menit_i2_b = selisih_i2_b.minute / 60
                        hour_i2_b = selisih_i2_b.hour
                        
                        jam_i2_b = int(hour_i2_b) + float(menit_i2_b) + float(detik_i2_b)
                        
                        tji2_b = jam_i2_b                   
                    else:
                        
                        if int(ab.pegawai.status.id) == 3:
                            tplus_b = ab.tgl_absen + timedelta(days=1)
                        else:
                            tplus_b = ab.tgl_absen
                        
                        dist2_b = f'{ab.tgl_absen} {ab.istirahat2_b}'
                        dkmb2_b = f'{tplus_b} {ab.kembali2_b}'
                        
                        ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
                        kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih_i2_b = kmb2_b - ist2_b
                        djam_selisih_i2_b = f'{ab.tgl_absen} {dselisih_i2_b}'
                        selisih_i2 = datetime.strptime(djam_selisih_i2_b, '%Y-%m-%d %H:%M:%S')
                            
                        detik_i2_b = selisih_i2_b.second / 3600
                        menit_i2_b = selisih_i2_b.minute / 60
                        hour_i2_b = selisih_i2_b.hour
                        
                        jam_i2_b = int(hour_i2_b) + float(menit_i2_b) + float(detik_i2_b)
                        
                        tji2_b = jam_i2_b
                else:
                    tji2_b = 0    
                ab.total_jam_kerja = tjk + tjk_b
                ab.total_jam_istirahat = tji + tji_b
                ab.total_jam_istirahat2 = tji2 + tji2_b
                ab.save()
                    
            else:
                pass            
    return JsonResponse({"ok":"ok"})
    # return redirect ('cabsen_s',dr=dr, sp=sp, sid=int(sid))   


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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        # print(sid_lembur.id)
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
            elif int(sid) == p.status_id:     
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
            'sil': sid_lembur,
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(request,'hrd_app/ijin/[sid]/ijin.html', data)
        
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

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
            'sil': sid_lembur,
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(request,'hrd_app/ijin/cijin/[dr]/[sp]/[sid]/cijin.html', data)
        
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

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
            'sil': sid_lembur,
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(request,'hrd_app/ijin/cijin/[dr]/[sp]/[sid]/cijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def ijin_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        print(sid,"SID")
        for i in ijin_db.objects.select_related('pegawai','ijin').filter(tgl_ijin__range=(dari,sampai)):
            if int(sid) == 0:
                
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
            elif int(sid) == i.pegawai.status_id:
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
                pass
                
                                
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
    try:
        ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=tgl)
    except:
        return JsonResponse({"status": "error"})
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

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
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/geser_off/[sid]/geser_off.html', data)
        
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
        print(dr,"DARI")
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

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
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/geser_off/[dr]/[sp]/[sid]/cgeser_off.html', data)
        
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

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
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/geser_off/[dr]/[sp]/[sid]/cgeser_off.html', data)
        
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

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
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'OPG'
        }
        
        return render(request,'hrd_app/opg/opg/[sid]/opg.html', data)
        
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

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
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'OPG'
        }
        
        return render(request,'hrd_app/opg/copg/[dr]/[sp]/[sid]/copg.html', data)
        
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

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
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'OPG'
        }
        
        return render(request,'hrd_app/opg/copg/[dr]/[sp]/[sid]/copg.html', data)
        
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
    else:
        status = "data absensi tidak ada"     
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
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
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
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/cuti/[sid]/cuti.html', data)
        
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        
        ac = awal_cuti_db.objects.last()
        tac = ac.tgl       
        
        data = {
            'akses' : akses,
            'idp' : idp,
            'dsid': dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari': tac,
            'sampai': today,
            'nama_pegawai':pg.nama,
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/cuti/[sid]/[idp]/detail_cuti.html', data)
        
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
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        data = {
            'akses' : akses,
            'idp' : idp,
            'dsid': dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari': dari,
            'sampai': sampai,
            'nama_pegawai':pg.nama,
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/cuti/[sid]/[idp]/detail_cuti.html', data)
        
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
    print(idp,"SDSD")
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
                                        tplus = ab.tgl_absen         
                            
                                        dmsk = f'{ab.tgl_absen} {ab.masuk}'
                                        dplg = f'{tplus} {ab.pulang}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                        date_part, delta_part, time_part = djam_selisih.split(' ', 2)
                                        # Parse the date and time
                                        base_datetime = datetime.strptime(date_part + ' ' + time_part.split(",")[1], '%Y-%m-%d %H:%M:%S')

                                        # Adjust the date based on the delta part
                                        if delta_part == '-1':
                                            adjusted_datetime = base_datetime - timedelta(days=1)
                                        elif delta_part == '+1':
                                            adjusted_datetime = base_datetime + timedelta(days=1)
                                        else:
                                            adjusted_datetime = base_datetime
                                        selisih = datetime.strptime(str(adjusted_datetime), '%Y-%m-%d %H:%M:%S')
                                        
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
                                elif ab.masuk_b is not None and ab.pulang_b is not None:
                                    if ab.masuk_b < ab.pulang_b :
                                        dmsk = f'{ab.tgl_absen} {ab.masuk_b}'
                                        dplg = f'{ab.tgl_absen} {ab.pulang_b}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                        date_part, delta_part, time_part = djam_selisih.split(' ', 2)
                                        # Parse the date and time
                                        base_datetime = datetime.strptime(date_part + ' ' + time_part.split(",")[1], '%Y-%m-%d %H:%M:%S')

                                        # Adjust the date based on the delta part
                                        if delta_part == '-1':
                                            adjusted_datetime = base_datetime - timedelta(days=1)
                                        elif delta_part == '+1':
                                            adjusted_datetime = base_datetime + timedelta(days=1)
                                        else:
                                            adjusted_datetime = base_datetime
                                        selisih = datetime.strptime(str(adjusted_datetime), '%Y-%m-%d %H:%M:%S')
                                        
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
                                        tplus = ab.tgl_absen         
                            
                                        dmsk = f'{ab.tgl_absen} {ab.masuk_b}'
                                        dplg = f'{tplus} {ab.pulang_b}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                        selisih = datetime.strptime(str(djam_selisih), '%Y-%m-%d %H:%M:%S')
                                        
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
    
    if absensi_db.objects.filter(pegawai_id=idp, tgl_absen=tcuti).exists():
        ab = absensi_db.objects.get(pegawai_id=idp, tgl_absen=tcuti)
        ab.keterangan_absensi = None
        ab.save()
        
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"cuti-(a.n {pg.nama}, tgl:{tcuti})"
    )
    histori.save()   
    
    ct.delete()
    status = "ok"
        
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
        try:
            ids = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            ids = ids.status_pegawai.pk
        except:
            ids = 0
        status = status_pegawai_lembur_db.objects.all().values("status_pegawai_id","status_pegawai__status")
        if sid == 0:
            sid_lembur = status_pegawai_lembur_db.objects.all()
        else:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
        pegawai = []
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                if int(sid) == p.status.pk:
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
            else:
                if p.status_id == sid:     
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
            'sil': ids,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'prd':int(prd),
            'thn':int(thn),
            'nama_bulan':bln,
            'modul_aktif' : 'Lembur'
        }
        
        return render(request,'hrd_app/lembur/lembur/[sid]/lembur.html', data)
        
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
        
        status = status_pegawai_lembur_db.objects.all().values("status_pegawai_id","status_pegawai__status")
        sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
        pegawai = []
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                if int(sid) == p.status.pk:
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
            else:
                if p.status_id == sid:     
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
            'sil': sid_lembur.pk,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'prd':int(prd),
            'thn':int(thn),
            'nama_bulan':bln,
            'modul_aktif' : 'Lembur'
        }
        
        return render(request,'hrd_app/lembur/belum_proses/[sid]/belum_proses.html', data)
        
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
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
            if int(sid) == 0:
                if int(sid) == p.status.pk:
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
                if p.status_id == dsid:     
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
            'sil': sid_lembur,
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
            if (ab.jam_istirahat == 0 and ab.jam_istirahat is not None) or ab.jam_istirahat is None:
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
                                                                    
                        b_plg.append(mulai_plg)
                                                        
                        for x in range(int(looping) - 1):
                            a2_plg = b_plg[x] - timedelta(minutes=30)
                            b_plg.append(a2_plg)
                        if absen_pulang >= mulai_plg:
                            pemotong_plg = 0
                        else:
                            for b in b_plg:
                                if absen_pulang < b:
                                    pemotong_plg = (b_plg.index(b) + 1) * 0.5
                                else:
                                    pass 
                        print(pemotong_plg,"PEMOTONG PULANG")
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
                                    lama_ist = (ist_1 * int(Decimal(ab.lama_istirahat) * 60)) + 5                                     
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
                                    print(pemotong_ist,"PEMOTONG IST")
                            else:
                                # -------------------------------------------------
                                # istirahat 1
                                lama_ist = (ist_1 * int(Decimal(ab.lama_istirahat) * 60)) + 5                                     
                                
                                a_ist = absen_ist + timedelta(minutes=lama_ist)  
                                print(a_ist,"COBA")
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
                                    
                                    lama_ist2 = (ist_2 * int(Decimal(ab.lama_istirahat2) * 60)) + 5                                     
                                    print(Decimal(ab.lama_istirahat2))
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
                            pemotong_ist = Decimal(-ab.lama_istirahat)
                            pemotong_ist2 = Decimal(-ab.lama_istirahat2)

                            # additional perhitungan istirahat
                            # if ist_1 + ist_2 > 1:
                            #     selisih_pi = (ist_1+ist_2) - 1
                            #     pi = (pemotong_ist + pemotong_ist2) + selisih_pi
                            # else:
                        pi = pemotong_ist + pemotong_ist2
                        pemotong_msk = Decimal(pemotong_msk)
                        pi = Decimal(pi)
                        pemotong_plg = Decimal(pemotong_plg)
                        awal = Decimal(awal)
                        akhir = Decimal(akhir)
                        if awal > 0 and akhir > 0:
                            lembur = Decimal((awal + akhir)) - (pemotong_msk + pi + pemotong_plg)
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
        print(prd,thn)
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
        print(data,"DATA")
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
    print(dr,sp,prd,thn,"INI")
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
        
        return render(request,'hrd_app/status_pegawai/status_pegawai.html', data)
        
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
        
        return render(request,'hrd_app/divisi/divisi.html', data)
        
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
        
        return render(request,'hrd_app/libur_nasional/libur_nasional.html', data)
        
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
        print(kk)
        data = {       
            'dsid': dsid,
            'kk': kk,
            'modul_aktif' : 'Jam Kerja'     
        }
        
        return render(request,'hrd_app/jam_kerja/jam_kerja.html', data)
        
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
def edit_kk_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        ekk = request.POST.get('ekk')
        new_kk = request.POST.get('new_kk')
        try:
            if kelompok_kerja_db.objects.filter(~Q(pk=int(ekk)),kelompok=new_kk).exists():
                return JsonResponse({"status": "duplikat"})
            print(ekk)
            kelompok_kerja_db.objects.filter(pk=int(ekk)).update(kelompok=new_kk)
            return JsonResponse({"status": "ok"})
        except: 
            return JsonResponse({"status": "gagal update",})
                                
        


@login_required
def jam_kerja_json(request):
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in jamkerja_db.objects.all().order_by('kk_id__kelompok'):            
            
            jk = {
                'id': i.id,
                'kk': i.kk_id,
                'kk_nama':i.kk.kelompok,
                'masuk': i.jam_masuk,
                'ist': i.jam_istirahat,
                'k_ist': i.jam_kembali_istirahat,
                'ist2': i.jam_istirahat2,
                'k_ist2': i.jam_kembali_istirahat2,
                'pulang': i.jam_pulang,
                'hari':i.hari
            }
            data.append(jk)
        print(data)
        return JsonResponse({"data": data})


@login_required
def tambah_jam_kerja(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        kk = r.POST.get("kk")
        jam_masuk = r.POST.get("jam_masuk")
        jam_istirahat = r.POST.get("jam_istirahat")
        jam_kistirahat = r.POST.get("jam_kistirahat")
        jam_istirahat2 = r.POST.get("jam_istirahat2")
        jam_kistirahat2 = r.POST.get("jam_kistirahat2")
        jam_pulang = r.POST.get("jam_pulang")
        hari = r.POST.getlist("hari[]")


        # try:
        #     # index = hari.index("Semua Hari")
        #     for 
        #     hari = [hari[index]]
        # except:
        #     hari = hari

        for h in hari:
            if h.lower() == 'semua hari':
                hari = ["Semua Hari"]
                break
                


        if len(hari) >= 7:
            hari = ["Semua Hari"]


        if jamkerja_db.objects.filter(kk_id=int(kk),jam_masuk=jam_masuk,jam_pulang=jam_pulang).exists():
            status = "gagal tambah"
        else:
            print("SSD")
            for h in hari:
                # if jamkerja_db.objects.filter(kk_id=int(kk),hari=h).exists():
                #     continue
                
                if h.lower() == 'semua hari':
                    if jamkerja_db.objects.filter(~Q(hari='semua hari'),kk_id=int(kk)).exists():
                        break

                jamkerja_db(
                    kk_id=kk,
                    jam_masuk=jam_masuk,
                    jam_pulang=jam_pulang,
                    jam_istirahat=jam_istirahat,
                    jam_kembali_istirahat=jam_kistirahat,
                    jam_istirahat2=jam_istirahat2,
                    jam_kembali_istirahat2=jam_kistirahat2,
                    hari=h
                ).save()
            status = "ok"
        return JsonResponse({"status": status})


@login_required
def edit_jam_kerja(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = r.POST.get('id')
        jam_masuk = r.POST.get("jam_masuk")
        jam_pulang = r.POST.get("jam_pulang")
        jam_istirahat = r.POST.get("jam_istirahat")
        jam_istirahat2 = r.POST.get("jam_istirahat2")
        jam_kistirahat = r.POST.get("jam_kistirahat")
        jam_kistirahat2 = r.POST.get("jam_kistirahat2")
        kk = r.POST.get("kk")
        hari = r.POST.get("hari")
        try:
            get = jamkerja_db.objects.get(pk=int(eid))
            jamkerja_db.objects.filter(id=int(eid)).update(
                jam_masuk=jam_masuk,
                jam_pulang=jam_pulang,
                jam_istirahat=jam_istirahat,
                jam_kembali_istirahat=jam_kistirahat,
                jam_istirahat2=jam_istirahat2,
                jam_kembali_istirahat2=jam_kistirahat2,
                hari=hari,
                kk_id=int(kk)
            )
            print(r.POST)
            status = "Ok"
            return JsonResponse({"status": status})
        except:
            return JsonResponse({"status": "gagal update"})


@login_required
def hapus_jam_kerja(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
        
        try:
            ln = jamkerja_db.objects.get(id=int(hid))           
        except:
            return JsonResponse({'status':'gagal hapus'})

        thapus = histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus jam kerja : {ln.kk.kelompok}'
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
        
        return render(request,'hrd_app/ijin/jenis_ijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@login_required
def jenis_ijin_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        jenis_ijin = jenis_ijin_db.objects.all()
        
        data = []

        for j in jenis_ijin:
            obj = {
                "pk":j.pk,
                "jenis_ijin":j.jenis_ijin
            }
            data.append(obj)
        return JsonResponse({"data":data},safe=False,status=200)

@login_required
def tjenis_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")

    if jenis_ijin_db.objects.filter(jenis_ijin=jenis_ijin).exists():
        status="duplikat"
    else:
        jenis_ijin_db(
            jenis_ijin=jenis_ijin
        ).save()
        status = "ok"
    return JsonResponse({"status":status},safe=False,status=200)

@login_required
def ejenis_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")
    id = r.POST.get("id") 
    if jenis_ijin_db.objects.filter(~Q(id=int(id)),jenis_ijin=jenis_ijin).exists():
        status = "duplikat"
    else:
        jenis_ijin_db.objects.filter(id=int(id)).update(jenis_ijin=jenis_ijin)
        status = "ok"
    return JsonResponse({"status":status},safe=False,status=200)

@login_required
def hjenis_ijin(r):
    id = r.POST.get("id")
    jenis_ijin = r.POST.get("jenis_ijin")
    nama_user = r.user.username
    try:
        jenis_ijin_db.objects.get(pk=int(id)).delete()
        thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus jenis ijin : {jenis_ijin}'
        )
        thapus.save()
        status = 'Ok'
    except:
        status = "gagal menghapus" 
    return JsonResponse({"status":status},safe=False,status=200)


@login_required
def status_pegawai_lembur(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        status_pegawai = status_pegawai_db.objects.all()
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            "status":status_pegawai,
            'modul_aktif' : 'Status Pegawai Lembur'     
        }
        
        return render(request,'hrd_app/status_pegawai/status_pegawai_lembur/status_pegawai_lembur.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

    
@login_required
def tstatus_pegawai_lembur(r):
    status = r.POST.get("status")
    
    if status_pegawai_lembur_db.objects.filter(status_pegawai_id=status).exists():
        return JsonResponse({'status':'duplikat'},safe=False,status=400)
    else:
        print(status)
        status_pegawai_lembur_db(status_pegawai_id=int(status)).save()
        return JsonResponse({'status':'berhasil'},safe=False,status=201)

@login_required
def status_pegawai_lembur_json(r):
    result = status_pegawai_lembur_db.objects.all()
    data = []
    for r in result:
        obj = {
            'status_pegawai':r.status_pegawai.status,
            'pk':r.pk,
            "status_id":r.status_pegawai_id
        }
        data.append(obj)
    
    return JsonResponse({"data":data},status=200,safe=False)

@login_required
def estatus_pegawai_lembur(r):
    status = r.POST.get("status")
    id = r.POST.get('id')

    try:
        get = status_pegawai_lembur_db.objects.get(pk=int(id))
        status_pegawai_lembur_db.objects.filter(pk=int(id)).update(status_pegawai_id=int(status))
        return JsonResponse({'status':'ok'},safe=False,status=200)
    except:
        return JsonResponse({"status":"gagal update"},safe=False,status=400)

@login_required
def hstatus_pegawai_lembur(r):
    id = r.POST.get('id')
    nama_user = r.user.username
    try:
        get = status_pegawai_lembur_db.objects.get(pk=int(id))
        histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus status pegawai lembur : {get.status_pegawai.status}'
        )
        status_pegawai_lembur_db.objects.get(pk=int(id)).delete()
        return JsonResponse({'status':'ok'},safe=False,status=200)
    except:
        return JsonResponse({"status":"gagal hapus"},safe=False,status=400)

