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

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Pegawai

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

