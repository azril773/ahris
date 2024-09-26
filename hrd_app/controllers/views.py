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
    logout(request)
    return redirect("login")
        
# Home
@login_required
def beranda(request):  
    
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses        
        dsid = dakses.sid_id
        print(dsid,"COBA")
        
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