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
import re
# PYZK / FINGER MACHINE
from zk import ZK, const
from struct import pack
from zk import user as us
import codecs  
# MODEL / DATABASE
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
        
# Home
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
        r.session["ccabang"] = cabang
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