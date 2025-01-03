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
from hrd_app.function import prosesabsensi
from openpyxl.styles import Alignment, Font
from collections import namedtuple
from openpyxl import Workbook
import math
import json
import time
import pandas as pd
from decimal import *
import re
# PYZK / FINGER MACHINE
from zk import ZK, const
from struct import pack
from zk import user as us
import codecs  
# MODEL / DATABASE
import hrd_app as app
from ..models import *
from django.core.serializers import serialize # Create your views here.


# Functions


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Dispatch & Login
@login_required
def logindispatch(request):
    request.POST.get('next')


# Logout
def user_logout(request):
    request.session["ccabang"] = None
    request.session["cabang"] = None
    logout(request)
    return redirect("login")
         
@login_required
def beranda(r):  
    
    iduser = r.user.id
    print("KLKL")
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses        
        dsid = dakses.sid_id
        
        today = date.today()
        print("OKK")
        data = {
            'akses' : akses,
            'today' : today,
            'dsid' : dsid,
        }
        
        return redirect("absensi",sid=dsid)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('login')


@login_required
def beranda_no_akses(request):    

    messages.info(request, 'Data akses Anda belum di tentukan.')        
    return redirect('beranda')




@login_required
def ganti_cabang(r):
    cabang = r.POST.get("cabang")
    if not cabang_db.objects.filter(cabang=cabang).exists():
        return JsonResponse({"status":"error","msg":"Gagal mengganti cabang"},status=401)
    cabang = cabang_db.objects.filter(cabang=cabang)
    if akses_cabang_db.objects.filter(cabang_id=cabang[0].pk).exists():
        r.session["ccabang"] = cabang[0].cabang
        return JsonResponse({"status":"success","msg":"Berhasil mengganti cabang"},status=200)
    else:
        return JsonResponse({"status":"error","msg":"Gagal mengganti cabang"},status=401)

# +++++++++++++++++++++++++++ PEGAWAI ++++++++++++++++++++++++++++++++
from hrd_app.controllers.pegawai.views import *

# +++++++++++++++++++++++++++ ABSENSI ++++++++++++++++++++++++++++++++
from hrd_app.controllers.absensi.views import *

# +++++++++++++++++++++++++++ IJIN ++++++++++++++++++++++++++++++++
from hrd_app.controllers.ijin.views import *

# +++++++++++++++++++++++++++ CUTI ++++++++++++++++++++++++++++++++
from hrd_app.controllers.cuti.views import *

# +++++++++++++++++++++++++++ JAM KERJA ++++++++++++++++++++++++++++++++
from hrd_app.controllers.jam_kerja.views import *

# +++++++++++++++++++++++++++ COUNTER ++++++++++++++++++++++++++++++++
from hrd_app.controllers.counter.views import *

# +++++++++++++++++++++++++++ DIVISI ++++++++++++++++++++++++++++++++
from hrd_app.controllers.divisi.views import *

# +++++++++++++++++++++++++++ STATUS PEGAWAI ++++++++++++++++++++++++++++++++
from hrd_app.controllers.status_pegawai.views import *

# +++++++++++++++++++++++++++ GESER OFF ++++++++++++++++++++++++++++++++
from hrd_app.controllers.geser_off.views import *

# +++++++++++++++++++++++++++ LEMBUR ++++++++++++++++++++++++++++++++
from hrd_app.controllers.lembur.views import *

# +++++++++++++++++++++++++++ LIBUR NASIONAL ++++++++++++++++++++++++++++++++
from hrd_app.controllers.libur_nasional.views import *

# +++++++++++++++++++++++++++ OPG ++++++++++++++++++++++++++++++++
from hrd_app.controllers.opg.views import *

# +++++++++++++++++++++++++++ LAPORAN ++++++++++++++++++++++++++++++++
from hrd_app.controllers.laporan.views import *

from hrd_app.controllers.broadcast.views import *

from hrd_app.controllers.mesin.views import *


from hrd_app.controllers.login.views import *

from hrd_app.controllers.ypc.views import *

from hrd_app.controllers.shift.views import *

from hrd_app.controllers.pkwt.views import *

# df = pd.read_csv("absensi.csv")
#     data = []
#     userids = []
#     for index, row in df.iterrows():
#         ka = None
#         ki = None
#         if str(row["keterangan"]) != "nan" or str(row["ubah_keterangan"]) != "nan":
#             # print(row)
#             regex = re.compile(r"(dispensasi)|(sakit)|(dinas)|(ijin)",re.IGNORECASE)
#             if regex.match(str(row["keterangan"])) is not None or regex.match(str(row["ubah_keterangan"])) is not None:
#                 if str(row["keterangan"]) == "nan":
#                     ki = str(row["ubah_keterangan"])
#                 elif str(row["ubah_keterangan"]) == "nan":
#                     ki = str(row["keterangan"])
#                 else:
#                     ki = str(row["keterangan"])+str(row["ubah_keterangan"])
#             else:
#                 if str(row["keterangan"]) == "nan":
#                     ki = str(row["ubah_keterangan"])
#                 elif str(row["ubah_keterangan"]) == "nan":
#                     ki = str(row["keterangan"])
#                 else:
#                     ki = str(row["keterangan"])+str(row["ubah_keterangan"])
#         obj = {
#             "userid":row["userid"],
#             "tgl_absen":row["tgl_absen"],
#             "masuk":str(row["masuk"]).split(" ")[-1] if str(row["masuk"]) != "nan" else None,
#             "istirahat":str(row["istirahat"]).split(" ")[-1] if str(row["istirahat"]) != "nan" else None,
#             "kembali":str(row["kembali"]).split(" ")[-1] if str(row["kembali"]) != "nan" else None,
#             "istirahat2":str(row["istirahat2"]).split(" ")[-1] if str(row["istirahat2"]) != "nan" else None,
#             "kembali2":str(row["kembali2"]).split(" ")[-1] if str(row["kembali2"]) != "nan" else None,
#             "keterangan_absensi":ka,
#             "keterangan_ijin":ki,
#             "total_jam_kerja":str(row["lama_kerja"]) if str(row["lama_kerja"]) != "nan" else None,
#             "pulang":str(row["pulang"]).split(" ")[-1] if str(row["pulang"]) != "nan" else None,
#         }
#         userids.append(row["userid"])
#         data.append(obj)
#     dr = sorted(data,key=lambda e: e["tgl_absen"])
#     pegawai = pegawai_db.objects.using(request.session["ccabang"]).filter(userid__in=userids)
#     # print(pegawai)
#     absensi = absensi_db.objects.using(request.session["ccabang"]).all()
#     for pgw in pegawai:
#         for dt in dr:
#             if int(dt["userid"]) == int(pgw.userid):
#                 cek = [ab for ab in absensi if ab.tgl_absen == dt["tgl_absen"]]
#                 if len(cek) > 0:
#                     continue
#                 else:
#                     absensi_db(
#                         tgl_absen=dt["tgl_absen"],
#                         masuk=dt["masuk"],
#                         istirahat=dt["istirahat"],
#                         kembali=dt["kembali"],
#                         istirahat2=dt["istirahat2"],
#                         kembali2=dt["kembali2"],
#                         keterangan_absensi=dt["keterangan_absensi"],
#                         keterangan_ijin=dt["keterangan_ijin"],
#                         total_jam_kerja=dt["total_jam_kerja"],
#                         pulang=dt["pulang"],
#                         pegawai_id=pgw.pk
#                     ).save(using=request.session["ccabang"])
#                 # print(dt['userid'])

from django.core.serializers import serialize # Create your views here.
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Pegawai

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
scheduler = BackgroundScheduler()

def tasiksetabsensi():
    try:
        today = datetime.now()
        print(today)
        dari = today
        sampai = today + timedelta(days=2)
        rangetgl = pd.date_range(dari, sampai).tolist()
        luserid = []
        pegawai = []
        for p in pegawai_db.objects.using("cirebon").select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").all():
                if p.jabatan is None:
                    jabatan = None
                else:
                    jabatan = p.jabatan.jabatan
                
                if p.counter is None:
                    counter = None
                else:
                    counter = p.counter.counter

                if p.divisi is None:
                    divisi = None
                else:
                    divisi = p.divisi.divisi

                if p.kelompok_kerja is None:
                    kelompok_kerja = None
                else:
                    kelompok_kerja = p.kelompok_kerja.kelompok
                    
                if p.hari_off2 is None:
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
                    'divisi' : divisi,
                    'jabatan' : jabatan,                
                    'hari_off' : p.hari_off.hari,
                    'hari_off2' : ho,
                    'kelompok_kerja' : kelompok_kerja,
                    'sisa_cuti' : p.sisa_cuti,
                    'shift' : p.shift,
                    'counter' : counter
                }
                luserid.append(p.userid)
                pegawai.append(data)
                for tgl in rangetgl:
                    if absensi_db.objects.using('cirebon').filter(tgl_absen=tgl.date(), pegawai_id=p.pk).exists():
                        pass
                    else:
                        absensi_db(
                            tgl_absen = tgl.date(),
                            pegawai_id = p.pk
                        ).save(using='cirebon')
        dr = datetime.now() - timedelta(days=1)
        sp = dr + timedelta(days=1)
        dari = datetime.strptime(datetime.strftime(dr,"%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")
        sampai = datetime.strptime(datetime.strftime(sp,"%Y-%m-%d 00:00:00"),"%Y-%m-%d %H:%M:%S")
        dmesin = []
        for m in mesin_db.objects.using('cirebon').filter(status='Active'):
            print(m)
            ip = m.ipaddress
            # conn = None
            zk = ZK(str(ip), port=4370, timeout=65)

            try:
                conn = zk.connect()
                conn.disable_device()
                # Data absensi
                absensi = conn.get_attendance()
                # print(absensi)
                for a in absensi:
                    if dari <= a.timestamp <= sampai:   
                        # users = conn.get_users()
                        if str(a.user_id) in luserid:     
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
                conn.disconnect()
            except Exception as e:
                # print(e)
                raise Exception("Terjadi kesalahan")
        att = sorted(dmesin, key=lambda i: i['jam_absen'])

        ddr = []
        # jika istirahat sama maka jan masukin ke b INGETTTT
        
            
        # ambil data raw simpan di ddr
        for d in data_raw_db.objects.using("cirebon").filter(userid__in=luserid,jam_absen__range=(dari - timedelta(days=1),sampai + timedelta(days=1))):
            data = {
                "userid": d.userid,
                "jam_absen": str(d.jam_absen),
                "punch": d.punch,
                "mesin": d.mesin
            }

            ddr.append(data)              
        
        ddt = []
        ddtor = []
        
        # ambil data trans simpan di ddt
        for d2 in data_trans_db.objects.using("cirebon").filter(userid__in=luserid,jam_absen__range=(dari - timedelta(days=1),sampai + timedelta(days=1))):
            data = {
                "userid": d2.userid,
                "jam_absen": d2.jam_absen,
                "punch": d2.punch,
                "mesin": d2.mesin,
                "ket": d2.keterangan
            }
            ddtor.append(data)
            ddt.append(data)
            
        status_lh = [st.status_pegawai.pk for st in status_pegawai_lintas_hari_db.objects.using("cirebon").all()]
        # proses data simpan di dt array
        # obj 
        jamkerja = jamkerja_db.objects.using("cirebon").select_related('kk').all()
        now = datetime.now()
        hari = now.strftime("%A")
        hari = nama_hari(hari)


        prosesabsensi.nlh(att,luserid,ddr,rangetgl,pegawai,jamkerja,status_lh,hari,"cirebon",ddt,ddtor)

        ijin = []  
        libur = []
        cuti = []
        geser = []
        geser_all = []
        kompen = []
        opg = []
        lmbr = []
        opg_all = []
        dl = []
        dl_idp = []
        ijindl = []
        lsopg = []
        
        # list status pegawai yang dapat opg
        for s in list_status_opg_db.objects.using("cirebon").all():
            lsopg.append(s.status_id)
        
        # geser off all 
        for ga in geseroff_db.objects.using("cirebon").all():
            data = {
                'id' : ga.id,
                'idp' : ga.pegawai_id, 
                'dari_tgl' : ga.dari_tgl,
                'ke_tgl' : ga.ke_tgl,
                'keterangan' : ga.keterangan
            } 
            geser_all.append(data)

        # opg all
        for oa in opg_db.objects.using("cirebon").all():
            data = {
                'id':oa.id,
                'idp': oa.pegawai_id,
                'opg_tgl':oa.opg_tgl,
                'diambil_tgl':oa.diambil_tgl,
                'keterangan':oa.keterangan
            }
            opg_all.append(data)


        # data ijin
        for i in ijin_db.objects.using("cirebon").select_related('ijin','pegawai').filter(tgl_ijin__range=(dari.date(),sampai.date())):
            data = {
                "ijin" : i.ijin.jenis_ijin,
                "tgl_ijin" : i.tgl_ijin,
                "idp" : i.pegawai_id,
                "keterangan" : i.keterangan
            }
            ijin.append(data)
        
        # data libur nasional
        for l in libur_nasional_db.objects.using("cirebon").filter(tgl_libur__range=(dari.date(),sampai.date())):
            data = {
                'libur' : l.libur,
                'tgl_libur' : l.tgl_libur,
                'insentif_karyawan' : l.insentif_karyawan,
                'insentif_staff' : l.insentif_staff
            }    
            libur.append(data)  
            
        # data cuti
        for c in cuti_db.objects.using("cirebon").select_related('pegawai').filter(tgl_cuti__range=(dari.date(),sampai.date())):
            data = {
                'id': c.id,
                'idp' : c.pegawai_id,
                'tgl_cuti' : c.tgl_cuti,
                'keterangan' : c.keterangan
            }                
            cuti.append(data)
            
        # data geser off
        for g in geseroff_db.objects.using("cirebon").select_related('pegawai').filter(ke_tgl__range=(dari.date(),sampai.date())):
            data = {
                'id' : g.id,
                'idp' : g.pegawai_id, 
                'dari_tgl' : g.dari_tgl,
                'ke_tgl' : g.ke_tgl,
                'keterangan' : g.keterangan
            } 
            geser.append(data)
        status_ln = [st.status.pk for st in list_status_opg_libur_nasional_db.objects.using("cirebon").all()]
        # data opg
        for o in opg_db.objects.using("cirebon").select_related('pegawai').filter(diambil_tgl__range=(dari.date(),sampai.date()), status=0):
            data = {
                'id':o.id,
                'idp': o.pegawai_id,
                'opg_tgl':o.opg_tgl,
                'diambil_tgl':o.diambil_tgl,
                'keterangan':o.keterangan
            }
            opg.append(data)
        
        # data dinas luar
        for n in dinas_luar_db.objects.using("cirebon").select_related('pegawai').filter(tgl_dinas__range=(dari.date(),sampai.date())):
            data = {
                'idp': n.pegawai_id,
                'tgl_dinas':n.tgl_dinas,
                'keterangan':n.keterangan
            }
            dl.append(data)
            dl_idp.append(n.pegawai_id)
        dariij = dari - timedelta(days=1)
        sampaiij = sampai + timedelta(days=1)
        for ij in ijin_db.objects.using("cirebon").filter(tgl_ijin__range=(dariij.date(),sampaiij.date())):
            if re.search('(dinas luar|dl)',ij.ijin.jenis_ijin,re.IGNORECASE) is not None:
                data = {
                    "tgl":ij.tgl_ijin,
                    "idp":ij.pegawai.pk,
                    "ijin":ij.ijin
                }
                ijindl.append(data)


        for k in kompen_db.objects.using("cirebon").all():
            data = {
                "idl":k.pk,
                "idp":k.pegawai_id,
                "jenis_kompen":k.jenis_kompen,
                "kompen":k.kompen,
                "tgl_kompen":k.tgl_kompen,
            }
            kompen.append(data)
            
        # data absensi
        data = absensi_db.objects.using("cirebon").select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen__range=(dari,sampai))
        cache = []
        for a in data:
            day = a.tgl_absen.strftime("%A")
            nh = nama_hari(day)        
            
            # for p in pegawai:
            #     if a.pegawai_id == p['idp']:
            ab = a 
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
            # jika ada absen masuk dan pulang
            # rencana cronjob jalan
            if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                if str(a.pegawai.hari_off) == str(nh):
                    # jika dia bisa mendapatkan opg 
                    # if 
                    #     continue
                    if a.pegawai.status_id in lsopg:
                        if re.search("security",a.pegawai.status.status,re.IGNORECASE) is not None:
                            pass
                        else:
                            # jika ada geder off dari hari ini ke hari lain
                            if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                                pass
                            # jika tidak ada
                            else:
                                
                                if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                                    pass
                                # jika tidak
                                else:
                                    opg_db(
                                        pegawai_id = ab.pegawai_id,
                                        opg_tgl = ab.tgl_absen,   
                                        keterangan = 'OFF Pengganti Reguler',                         
                                        add_by = 'Program',
                                    ).save(using="cirebon")
                    else:
                        pass
                else:
                    pass
                
                # sama aja kaya sebelumnya
                if str(a.pegawai.hari_off2) == str(nh):
                    if a.pegawai.status_id in lsopg:
                        if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                            pass
                        else:
                            if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                                pass
                            else:
                                opg_db(
                                    pegawai_id = ab.pegawai_id,
                                    opg_tgl = ab.tgl_absen,   
                                    keterangan = 'OFF Pengganti Reguler',                         
                                    add_by = 'Program',
                                ).save(using="cirebon")
                    else:
                        pass
                else:
                    pass
                    
                if str(a.pegawai.hari_off) == "On Off":
                    ab.keterangan_absensi = None
                    ab.save(using="cirebon")
                        
            # jika tidak ada masuk dan pulang   
            else:
                # jika dinas luar
                if len(ijindl) > 0:
                    for il in ijindl:
                        if il["tgl"] == ab.tgl_absen and int(il["idp"]) == int(ab.pegawai.pk):
                            # jika off dia hari ini
                            if str(a.pegawai.hari_off) == str(nh):
                                # jika dia bisa mendapatkan opg
                                if a.pegawai.status_id in lsopg:
                                    # jika dia geser dari hari off ke hari lain
                                    if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                                        pass
                                    # jika dia tidak geser dari hari off ke hari lain
                                    else:
                                        # ini rencana jika cronjob jalan
                                        if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                                            pass
                                        else:
                                            # ini kalo tidak jalan
                                            opg_db(
                                                pegawai_id = ab.pegawai_id,
                                                opg_tgl = ab.tgl_absen,   
                                                keterangan = 'OFF Pengganti Reguler',                         
                                                add_by = 'Program',
                                            ).save(using="cirebon")
                                else:
                                    pass
                            else:
                                # jika on off
                                if str(a.pegawai.hari_off) == 'On Off':
                                    ab.keterangan_absensi = 'OFF'
                                    ab.save(using="cirebon")
                                else:
                                    pass
                                
                            if str(a.pegawai.hari_off2) == str(nh):
                                if a.pegawai.status_id in lsopg:
                                    if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                                        pass
                                    else:
                                        if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                                            pass
                                        else:
                                            opg_db(
                                                pegawai_id = ab.pegawai_id,
                                                opg_tgl = ab.tgl_absen,   
                                                keterangan = 'OFF Pengganti Reguler',                         
                                                add_by = 'Program',
                                            ).save(using="cirebon")
                                else:
                                    pass
                            else:
                                pass  
                        else:
                            if (a.masuk is not None or a.pulang is not None) or (a.masuk_b is not None or a.pulang_b is not None):
                                if str(a.pegawai.hari_off) == "On Off":
                                    ab.keterangan_absensi = None
                                    ab.save(using="cirebon")
                            else:
                                if str(a.pegawai.hari_off) == str(nh):
                                    ab.keterangan_absensi = 'OFF'
                                    ab.save(using="cirebon")
                                elif str(a.pegawai.hari_off) == 'On Off':
                                    ab.keterangan_absensi = 'OFF'
                                    ab.save(using="cirebon")    
                                            
                                if str(a.pegawai.hari_off2) == str(nh):
                                    ab.keterangan_absensi = 'OFF'
                                    ab.save(using="cirebon") 
                                else:
                                    pass  
                else:
                    # jika dia hari ini off
                    if (a.masuk is not None or a.pulang is not None) or (a.masuk_b is not None or a.pulang_b is not None):
                        if str(a.pegawai.hari_off) == "On Off":
                            ab.keterangan_absensi = None
                            ab.save(using="cirebon")
                    else:
                        if str(a.pegawai.hari_off) == str(nh):
                            ab.keterangan_absensi = 'OFF'
                            ab.save(using="cirebon")
                        elif str(a.pegawai.hari_off) == 'On Off':
                            ab.keterangan_absensi = 'OFF'
                            ab.save(using="cirebon")    
                                    
                        if str(a.pegawai.hari_off2) == str(nh):
                            ab.keterangan_absensi = 'OFF'
                            ab.save(using="cirebon") 
                        else:
                            pass   
                # jika hari ini dia adalah off nya
            
            # libur nasional
            for l in libur:
            # jika ada absen di hari libur nasional
                ab.libur_nasional = None
                if l['tgl_libur'] == ab.tgl_absen:                            
                    ab.libur_nasional = l['libur']
                    ab.save(using="cirebon")
                    
                    # Hari Minggu
                    if str(nh) == 'Minggu':
                        if a.pegawai.status_id in lsopg:
                            
                            # Staff
                            if a.pegawai.status_id in status_ln: # regex
                                # jika hari off nya adalah hari minggu dan masuk maka hanya akan mendapatkan 1 opg
                                if str(a.pegawai.hari_off) == str(nh):
                                    if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                                        if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                                            pass
                                        else:
                                            if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                                                pass
                                            else:
                                                opg_db(
                                                    pegawai_id = ab.pegawai_id,
                                                    opg_tgl = ab.tgl_absen,   
                                                    keterangan = 'OFF Pengganti Reguler',                         
                                                    add_by = 'Program',
                                                ).save(using="cirebon")
                                    else:
                                        pass    
                                else:
                                    pass
                            
                            # Karyawan
                            else:
                                pass
                                # if str(a.pegawai.hari_off) == str(nh):
                                #     if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                                #         if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                                #             pass
                                #         else:
                                #             if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                                #                 pass
                                #             else:
                                #                 opg_db(
                                #                     pegawai_id = ab.pegawai_id,
                                #                     opg_tgl = ab.tgl_absen,   
                                #                     keterangan = 'OFF Pengganti Reguler',                         
                                #                     add_by = 'Program',
                                #                 ).save(using="cirebon")
                                                
                                #                 # dicirebon tidak ada insentif dihari minggu jika masuk
                                #                 # ab.insentif = l['insentif_karyawan']
                                #                 # ab.save(using="cirebon")
                                #     else:
                                #         pass    
                                # else:
                                #     pass                                
                        else:
                            pass 
                    
                    # Bukan Hari Minggu
                    else:
                        if a.pegawai.status_id in lsopg:
                                                            
                            # Staff
                            if a.pegawai.status_id in status_ln:
                                if str(a.pegawai.hari_off) == str(nh):
                                    # JIKA DIA MASUK DIHARI MERAH DILIBUR REGULERNYA MAKA AKAN DAPAT 2 OPG
                                    if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                                        if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                                            pass
                                        else:
                                            if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                                                pass
                                            else:
                                                opg_db(
                                                    pegawai_id = ab.pegawai_id,
                                                    opg_tgl = ab.tgl_absen,   
                                                    keterangan = 'OFF Pengganti Reguler',                         
                                                    add_by = 'Program',
                                                ).save(using="cirebon")
                                                
                                            if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Tgl Merah"),False):
                                                pass
                                            else:    
                                                opg_db(
                                                    pegawai_id = ab.pegawai_id,
                                                    opg_tgl = ab.tgl_absen,   
                                                    keterangan = 'OFF Pengganti Tgl Merah',                         
                                                    add_by = 'Program',
                                                ).save(using="cirebon")
                                    # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                                    else:
                                        if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Tgl Merah"),False):
                                            pass
                                        else:    
                                            opg_db(
                                                pegawai_id = ab.pegawai_id,
                                                opg_tgl = ab.tgl_absen,   
                                                keterangan = 'OFF Pengganti Tgl Merah',                         
                                                add_by = 'Program',
                                            ).save(using="cirebon")    
                                # JIKA HARI OFF TIDAK BERTEPATAN HARI LIBUR NASIONAL
                                else:
                                    if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                                        if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                                            pass
                                        else:
                                            if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Tgl Merah"),False):
                                                pass
                                            else:    
                                                opg_db(
                                                    pegawai_id = ab.pegawai_id,
                                                    opg_tgl = ab.tgl_absen,   
                                                    keterangan = 'OFF Pengganti Tgl Merah',                         
                                                    add_by = 'Program',
                                                ).save(using="cirebon")
                                    # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                                    else:
                                        pass
                            
                            # Karyawan
                            # JIKA MASUK HANYA MENDAPATKAN 1 OPG DAN INSENTIF
                            else:
                                # if str(a.pegawai.hari_off) == str(nh):
                                if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                                    if geseroff_db.objects.using("cirebon").filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
                                        pass
                                    else:
                                        
                                        if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                                            pass
                                        else:
                                            # opg_db(
                                            #     pegawai_id = ab.pegawai_id,
                                            #     opg_tgl = ab.tgl_absen,   
                                            #     keterangan = 'OFF Pengganti Reguler',                         
                                            #     add_by = 'Program',
                                            # ).save(using="cirebon")
                                            
                                            ab.insentif = l['insentif_karyawan']
                                            ab.save(using="cirebon")
                                else:
                                    pass    
                                # else:
                                #     pass                                
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
                        ab.save(using="cirebon")
                    else:
                        pass
                else:
                    pass                                 
            

            for kmpn in kompen:
                if a.pegawai_id == kmpn["idp"]:
                    if kmpn["tgl_kompen"] == a.tgl_absen:
                        print("OKOKO")
                        if ab.jam_masuk is not None and ab.jam_pulang is None:
                            if ab.masuk is not None and ab.pulang is not None:
                                if ab.pulang > ab.masuk:
                                    jm = datetime.combine(ab.tgl_absen,ab.jam_masuk)
                                    jp = datetime.combine(ab.tgl_absen,ab.jam_pulang)
                                    
                                    jkompen = float(kmpn["kompen"])
                                    
                                    if kmpn["jenis_kompen"] == 'awal':
                                        njm = jm - timedelta(hours=jkompen)
                                        njp = ab.jam_pulang
                                    elif kmpn["jenis_kompen"] == 'akhir':    
                                        njm = ab.jam_masuk
                                        njp = jp + timedelta(hours=jkompen)
                                    else:    
                                        njm = jm - timedelta(hours=jkompen)
                                        njp = jp + timedelta(hours=jkompen)
                                    
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
                                    ab.jam_masuk = njm
                                    ab.jam_pulang = njp
                                else: 
                                    # dmsk = f'{ab.tgl_absen} {ab.masuk}'
                                    # dplg = f'{ab.tgl_absen} {ab.pulang}'
                                    
                                    # msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                    # plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                    
                                    # dselisih = plg - msk
                                    # djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                    # date_part = djam_selisih.split(' ', 2)
                                    # # Parse the date and time
                                    # # Adjust the date based on the delta part
                                    # if len(date_part) > 2:
                                    #     base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                                    #     if date_part[1] == '-1':
                                    #         adjusted_datetime = base_datetime - timedelta(days=1)
                                    #     elif date_part[1] == '+1':
                                    #         adjusted_datetime = base_datetime + timedelta(days=1)
                                    # else:
                                    #     base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                                    #     adjusted_datetime = base_datetime     
                                    # selisih = adjusted_datetime
                                    # if int(selisih.hour) <= 4:
                                    #     tjk = 0
                                    # else:
                                    #     detik = selisih.second / 3600
                                    #     menit = selisih.minute / 60
                                    #     hour = selisih.hour
                                        
                                    #     jam = int(hour) + float(menit) + float(detik)
                                    #     tjk = jam  
                                    tjk = 0   
                            else:
                                tjk = 0
                        else:
                            tjk = 0
                        if kmpn["jenis_kompen"] == 'awal':
                            ab.keterangan_lain = f"Kompen/PJK-Awal {kmpn['kompen']} Jam"
                        elif kmpn["jenis_kompen"] == "akhir":
                            ab.keterangan_lain = f"Kompen/PJK-Akhir {kmpn['kompen']} Jam"
                        else:
                            ab.keterangan_lain = f"Kompen/PJK 1 hari"
                        nama_user = "prog"
                        ab.total_jam_kerja = round(tjk,1)
                        ab.edit_by = nama_user
                        ab.save(using="cirebon")

            

            # cuti
            for c in cuti:
                # jika didalam data cuti ada pegawai id
                if a.pegawai_id == c['idp']:
                    # jika tgl cuti sama dengan tgl absen
                    if c['tgl_cuti'] == ab.tgl_absen:
                        # jika tidak masuk dan pulang
                        if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
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
                                ab.save(using="cirebon")
                            # jika jam kerja lebih dari 4 jam
                            else:
                                cuti_db.objects.using("cirebon").get(id=int(c['id'])).delete()
                                pg = pegawai_db.objects.using("cirebon").get(pk=ab.pegawai_id)
                                sc = pg.sisa_cuti
                                ab.keterangan_absensi = ""
                                ab.save(using="cirebon")
                                pg.sisa_cuti = sc + 1
                                pg.save(using="cirebon")          
                        else:
                            ab.keterangan_absensi = c['keterangan']
                            ab.save(using="cirebon")
                    else:
                        pass
                else:
                    pass        
                
            # geser off
            for g in geser:
                if a.pegawai_id == g['idp']:
                    if g['ke_tgl'] == ab.tgl_absen:
                        # jika ada geser off dan dia tidak masuk
                        if (ab.masuk is None and ab.pulang is None) or (ab.masuk_b is None and ab.pulang_b is None):
                            drt = datetime.strftime(g['dari_tgl'], '%d-%m-%Y')
                            ab.keterangan_absensi = f'Geser OFF-({drt})' 
                            ab.save(using="cirebon")
                        # jika ada geser off dan dia masuk
                        else:
                            geseroff_db.objects.using("cirebon").get(id=int(g['id'])).delete()    
                    elif g["dari_tgl"] == ab.tgl_absen:
                        if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                            ab.keterangan_absensi = None
                            ab.save(using="cirebon")
                        else:
                            pass
                    else:
                        pass
            # opg
            for o in opg_all:
                if a.pegawai_id == o['idp']:
                    # cek jika di dalam data opg diambil pada tanggal saat ini
                    if o['diambil_tgl'] == ab.tgl_absen:
                        
                        opg_get= opg_db.objects.using("cirebon").get(id=o['id'])
                        # jika tidak masuk dan tidak ada pulang
                        if ab.masuk is None and ab.pulang is None and ab.masuk_b is None and ab.pulang_b is None:
                            topg = datetime.strftime(o['opg_tgl'], '%d-%m-%Y')
                            ab.keterangan_absensi = f'OPG-({topg})'
                            ab.save(using="cirebon")                                
                            
                            opg_get.status = 1
                            opg_get.edit_by ='Program'
                            opg_get.save(using="cirebon")
                        # jika masuk dan pulang
                        else:
                            opg_get.diambil_tgl = None
                            opg_get.edit_by = 'Program'
                            opg_get.save(using="cirebon")
                                
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
                        ab.save(using="cirebon")
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
                    date_part = djam_selisih.split(' ', 2)
                    # Parse the date and time
                    # Adjust the date based on the delta part
                    if len(date_part) > 2:
                        base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                        if date_part[1] == '-1':
                            adjusted_datetime = base_datetime - timedelta(days=1)
                        elif date_part[1] == '+1':
                            adjusted_datetime = base_datetime + timedelta(days=1)
                    else:
                        base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                        adjusted_datetime = base_datetime
                    selisih = adjusted_datetime
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
                    # if dselisih_b.hour < 10
                    djam_selisih_b = f'{ab.tgl_absen} {dselisih_b}'
                    date_part = djam_selisih_b.split(' ', 2)
                    # Split the string to separate the date and time parts
                    if len(date_part) > 2:
                        base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                        if date_part[1] == '-1':
                            adjusted_datetime = base_datetime - timedelta(days=1)
                        elif date_part[1] == '+1':
                            adjusted_datetime = base_datetime + timedelta(days=1)
                    else:
                        base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                        adjusted_datetime = base_datetime
                    selisih_b = adjusted_datetime
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
                    # Split the string to separate the date and time parts
                    date_part = djam_selisih_i.split(' ', 2)
                    # Parse the date and time
                    # Adjust the date based on the delta part
                    if len(date_part) > 2:
                        base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                        if date_part[1] == '-1':
                            adjusted_datetime = base_datetime - timedelta(days=1)
                        elif date_part[1] == '+1':
                            adjusted_datetime = base_datetime + timedelta(days=1)
                    else:
                        base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                        adjusted_datetime = base_datetime
                    selisih_i = adjusted_datetime
                        
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
                    # Split the string to separate the date and time parts
                    date_part = djam_selisih_i_b.split(' ', 2)
                    # Parse the date and time
                    # Adjust the date based on the delta part
                    if len(date_part) > 2:
                        base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                        if date_part[1] == '-1':
                            adjusted_datetime = base_datetime - timedelta(days=1)
                        elif date_part[1] == '+1':
                            adjusted_datetime = base_datetime + timedelta(days=1)
                    else:
                        base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                        adjusted_datetime = base_datetime
                    selisih_i_b = adjusted_datetime
                        
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
                    # Split the string to separate the date and time parts
                    date_part = djam_selisih_i2_b.split(' ', 2)
                    # Parse the date and time
                    # Adjust the date based on the delta part
                    if len(date_part) > 2:
                        base_datetime = datetime.strptime(date_part[0] + ' ' + date_part[2].split(",")[1], '%Y-%m-%d %H:%M:%S')
                        if date_part[1] == '-1':
                            adjusted_datetime = base_datetime - timedelta(days=1)
                        elif date_part[1] == '+1':
                            adjusted_datetime = base_datetime + timedelta(days=1)
                    else:
                        base_datetime = datetime.strptime(" ".join(date_part), '%Y-%m-%d %H:%M:%S')
                        adjusted_datetime = base_datetime
                    selisih_i2_b = adjusted_datetime
                        
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
            ab.save(using="cirebon")
            if ab.pegawai.counter is not None:
                ct = ab.pegawai.counter.counter
            else:
                ct = None

            if ab.pegawai.divisi is not None:
                dv = ab.pegawai.divisi.divisi
            else:
                dv = None

            if ab.pegawai.hari_off is not None:
                ho = ab.pegawai.hari_off.hari
            else:
                ho = None
        # pegawai_db.objects.using("cirebon").filter(pk=3636).update(
        #     nik=f'silvia-{datetime.now()}'
        # )
        print("SELESAI")
    except Exception as e:
        # print(e)
        return e
    # pegawai_db.objects.using("cirebon").filter(id=3636).update(nik="silvia21")
trigger = CronTrigger(
    year="*",month="*",day='*',hour="03",minute="00",second="00"
)
# trigger = CronTrigger(
#     year="*",month="*",day='*',hour="09",minute="27",second="45"
# )
# trigger1 = CronTrigger(
#     year="*",month="*",day='*',hour="03",minute="30",second="00"
# )
# trigger2 = CronTrigger(
#     year="*",month="*",day='*',hour="07",minute="00",second="00"
# )
# trigger3 = CronTrigger(
#     year="*",month="*",day='*',hour="07",minute="30",second="00"
# )
# scheduler.remove_all_jobs()
scheduler.add_job(tasiksetabsensi,trigger=trigger)
scheduler.start()
# scheduler.add_job(cirebonsetabsensi,trigger=trigger1)
# scheduler.add_job(cirebonsetabsensi,trigger=trigger2)
# scheduler.add_job(cirebonsetabsensi,trigger=trigger3)
