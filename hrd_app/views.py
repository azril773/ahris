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
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Pegawai

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
scheduler = BackgroundScheduler()

def tasiksetabsensi():
    today = datetime.now()
    dari = today
    sampai = today + timedelta(days=2)
    rangetgl = pd.date_range(dari.date(), sampai.date()).tolist()
    print("OKOKOK")
    for p in pegawai_db.objects.using("tasik").select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").all():
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
            for tgl in rangetgl:
                if absensi_db.objects.using('tasik').filter(tgl_absen=tgl, pegawai_id=p.pk).exists():
                    pass
                else:
                    absensi_db(
                        tgl_absen = tgl,
                        pegawai_id = p.pk
                    ).save(using='tasik')
trigger = CronTrigger(
    year="*",month="*",day='*',hour="14",minute="53",second="*"
)
scheduler.add_job(tasiksetabsensi,trigger=trigger)

