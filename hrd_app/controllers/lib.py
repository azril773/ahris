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
import weasyprint
from dateutil.relativedelta import relativedelta
from calendar import monthrange
# SUPPORT
from openpyxl.styles import Alignment, Font
from collections import namedtuple
import math
import json
import time
import pandas as pd
# import redis
import re
from decimal import *
from concurrent.futures import ThreadPoolExecutor
# PYZK / FINGER MACHINE
from zk import ZK, const
from struct import pack
from zk import user as us
import codecs  

# MODEL / DATABASE
from ..models import *
from django.core.serializers import serialize # Create your views here.




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
            
    dr=datetime.strptime(dr,'%Y-%m-%d')
    sp=datetime.strptime(sp,'%Y-%m-%d')
    prd = dperiode
    thn = dtahun
    
    data = (dr,sp,prd, thn)
    
    return data       

# Pengaturan
@login_required
def pengaturan(r):
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'dsid': dsid,  
            'modul_aktif' : 'Admin Panel'   
        }
        
        return render(r,'hrd_app/pengaturan/admin_panel.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

def terbilang(bil):
    angka = [
        "",
        "Satu",
        "Dua",
        "Tiga",
        "Empat",
        "Lima",
        "Enam",
        "Tujuh",
        "Delapan",
        "Sembilan",
        "Sepuluh",
        "Sebelas",
    ]
    Hasil = " "
    n = int(bil)
    if n >= 0 and n <= 11:
        Hasil = angka[n]
    elif n < 20:
        Hasil = terbilang(n - 10) + " Belas "
    elif n < 100:
        Hasil = terbilang(n / 10) + " Puluh " + terbilang(n % 10)
    elif n < 200:
        Hasil = " Seratus " + terbilang(n - 100)
    elif n < 1000:
        Hasil = terbilang(n / 100) + " Ratus " + terbilang(n % 100)
    elif n < 2000:
        Hasil = " Seribu " + terbilang(n - 1000)
    elif n < 1000000:
        Hasil = terbilang(n / 1000) + " Ribu " + terbilang(n % 1000)
    elif n < 1000000000:
        Hasil = terbilang(n / 1000000) + " Juta " + terbilang(n % 1000000)
    elif n < 1000000000000:
        Hasil = terbilang(n / 1000000000) + " Milyar " + terbilang(n % 1000000000)
    elif n < 1000000000000000:
        Hasil = (
            terbilang(n / 1000000000000) + " Triliyun " + terbilang(n % 1000000000000)
        )
    elif n < 1000000000000000000:
        Hasil = (
            terbilang(n / 1000000000000000) + " Kuadraliun " + terbilang(n % 1000000000000000)
        )
    else:
        Hasil = ":("

    return Hasil