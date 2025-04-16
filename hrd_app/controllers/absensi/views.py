from hrd_app.controllers.lib import *
import pika
# from numba import jit
import threading
from concurrent.futures import ThreadPoolExecutor
from django.db import connection
from multiprocessing import Pool
import ast
from hrd_app.function import prosesabsensi
import cProfile
 
# ++++++++++++++++++++++++++++ ++++++++++++++++++++++++++++++++
# Absensi 
@authorization(["*"])
def absensi(r,sid):
    iduser = r.session['user']['id']
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        
        today = datetime.today().date()
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        today = date.today()
        today_datetime = datetime.strptime(f'{today}','%Y-%m-%d')       
        tmin = datetime.strftime(today_datetime - timedelta(days=1),'%d-%m-%Y')
        
        dari = today
        sampai = today
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi).distinct("status_id"):
            statusid.append(p.status_id)
            # 
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")
        
        mesin = []
        for m in mesin_db.objects.using(r.session["ccabang"]).filter(status="Active"):
            mesin.append({"id":m.pk,"ipaddress":m.ipaddress,"nama":m.nama})

        sid_lembur = 0
        jenis_ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).all()   
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur,
            'dari': dari,
            'sampai': sampai,
            'tmin': tmin,
            'dr' : dr,
            'sp' : sp,
            "mesin":mesin,
            'jenis_ijin' : jenis_ijin,
            'modul_aktif' : 'Absensi'
        }

        return render(r,'hrd_app/absensi/absensi_non.html', data)
        
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    
@authorization(["*"])
def absensi_tgl(r,sid,dr,sp):
    iduser = r.session['user']['id']
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        
        today = datetime.today().date()
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        today = date.today()
        tdy = datetime.strftime(today,'%d-%m-%Y')
        
        # today = date.today()
        # today_datetime = datetime.strptime(f'{today}','%Y-%m-%d')       
        # tmin = today_datetime - timedelta(days=1)
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi).distinct("status_id"):
            statusid.append(p.status_id)
            # 
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")
        
        mesin = []
        for m in mesin_db.objects.using(r.session["ccabang"]).filter(status="Active"):
            mesin.append({"id":m.pk,"ipaddress":m.ipaddress,"nama":m.nama})

        sid_lembur = 0
        jenis_ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).all()  
        tmin = dr
        if dr == sp and dr == tdy and sp == tdy:
            tmin = datetime.strftime(today - timedelta(days=1),'%d-%m-%Y')
        print(tmin)
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur,
            "tmin": tmin,
            'dari': dari,
            'sampai': sampai,
            'dr' : dr,
            'sp' : sp,
            "mesin":mesin,
            'jenis_ijin' : jenis_ijin,
            'modul_aktif' : 'Absensi'
        }

        return render(r,'hrd_app/absensi/absensi_non.html', data)
        
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@authorization(["*"])
def cari_absensi(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        sid = r.POST.get('sid')
        dari = datetime.strptime(r.POST.get('ctgl1'),'%d-%m-%Y').date()
        sampai = datetime.strptime(r.POST.get('ctgl2'),'%d-%m-%Y').date()
        id_user = r.session['user']['id']
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        today = datetime.today().date()
        # 
        # 
        # red = redis.Redis(host="15.63.254.114", port="6370", decode_responses=True, username="azril", password=132)
        # if red.hgetall(f"absensi-{dari.strftime('%Y-%m-%d')}-{sampai.strftime('%Y-%m-%d')}-{sid}"):
        #     return JsonResponse({"data": json.loads(red.hgetall(f"absensi-{today}-{sid}")["data"]) })
        if int(sid) == 0:
            for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__counter','pegawai__divisi').filter(tgl_absen__range=(dari,sampai),pegawai__divisi__in=divisi).order_by('tgl_absen','pegawai__divisi__divisi'):
                sket = ""
                hari = a.tgl_absen.strftime("%A")
                hari_ini = nama_hari(hari) 
                
                if str(a.pegawai.counter) == "None":
                    bagian = f'{a.pegawai.divisi.divisi}'
                else:
                    bagian = f'{a.pegawai.divisi.divisi} - {a.pegawai.counter.counter}' 
                    
                if a.masuk is not None:
                    if a.jam_masuk is not None and a.masuk > a.jam_masuk:
                        msk = f"<span class='text-danger'>{a.masuk}</span>"
                    else:
                        msk = f"{a.masuk}"
                else:
                    msk = "-"

                if a.pulang is not None:
                    plg = f"{a.pulang}"
                else:
                    plg = "-"

                if a.masuk_b is not None:
                    msk_b = f"{a.masuk_b}"
                else:
                    msk_b = "-"

                if a.pulang_b is not None:
                    plg_b = f"{a.pulang_b}"
                else:
                    plg_b = "-"

                if a.istirahat is not None and a.istirahat2 is not None:
                    ist = f'{a.istirahat} / {a.istirahat2}'
                elif a.istirahat is not None and a.istirahat2 is None:                  
                    ist = f'{a.istirahat}'
                elif a.istirahat is None and a.istirahat2 is not None:                  
                    ist = f'{a.istirahat2}'
                else:
                    ist = "-"    

                if a.istirahat_b is not None and a.istirahat2_b is not None:
                    ist_b = f" {a.istirahat_b} / {a.istirahat2_b})"
                elif a.istirahat_b is not None and a.istirahat2_b is None:
                    ist_b = f" {a.istirahat_b}"
                elif a.istirahat_b is None and a.istirahat2_b is not None:
                    ist_b = f" {a.istirahat2_b}"
                else:
                    ist_b = "-"


                if a.lama_istirahat is not None and a.istirahat is not None:
                    jkembali = datetime.combine(a.tgl_absen,a.istirahat) + timedelta(hours=float(a.lama_istirahat))
                else:
                    jkembali = None
                if a.kembali is not None and a.kembali2 is not None:
                    if jkembali is not None and a.kembali > jkembali.time():
                        kmb = f'<span class="text-danger">{a.kembali}</span> / {a.kembali2}'
                    else:
                        kmb = f'{a.kembali} / {a.kembali2}'
                elif a.kembali is not None and a.kembali2 is None:                  
                    if jkembali is not None and a.kembali > jkembali.time():
                        kmb = f'<span class="text-danger">{a.kembali}</span>'
                    else:
                        kmb = f'{a.kembali}'
                elif a.kembali is None and a.kembali2 is not None:                  
                    kmb = f'{a.kembali2}'    
                else:
                    kmb = "-"        

                if a.kembali_b is not None and a.kembali2_b is not None:
                    kmb_b = f" {a.kembali_b} / {a.kembali2_b})"
                elif a.kembali_b is not None and a.kembali2_b is None:
                    kmb_b = f" {a.kembali_b}"
                elif a.kembali_b is None and a.kembali2_b is not None:
                    kmb_b = f" {a.kembali2_b}"
                else:
                    kmb_b = "-" 
                

                if a.keterangan_absensi is not None:
                    sket += f'{a.keterangan_absensi}, '                 
                if a.keterangan_ijin is not None:
                    sket += f'{a.keterangan_ijin}, '
                    kijin = ''
                else:
                    if not r.session["ccabang"] in ['cihideung','sumedang']:
                        if a.masuk is not None and a.jam_masuk is not None:
                            if a.masuk > a.jam_masuk:
                                sket += f"Terlambat masuk tanpa ijin, "

                if a.keterangan_lain is not None:
                    sket += f'{a.keterangan_lain}, '                    
                if a.libur_nasional is not None:
                    sket += f'{a.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if a.istirahat is not None and a.lama_istirahat is not None:
                    jmkem = a.lama_istirahat
                else:
                    jmkem = None
                if sket == "":
                    sket = "-"
                absen = {
                    'id': a.id,
                    'tgl': datetime.strftime(a.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    "tgl_absen":a.tgl_absen,
                    'nama': a.pegawai.nama,
                    'nik': a.pegawai.nik,
                    'userid': a.pegawai.userid,
                    'bagian': bagian,
                    "jam_masuk":a.jam_masuk,
                    "jam_pulang":a.jam_pulang,
                    'masuk': msk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': plg,
                    'masuk_b': msk_b,
                    'keluar_b': ist_b,
                    'kembali_b': kmb_b,
                    'pulang_b': plg_b,
                    "jam_kembali":jmkem,
                    'tj': a.total_jam_kerja,
                    'ket': sket,
                    'sln': sln,
                    'ln': a.libur_nasional
                }

                data.append(absen)
            
        else:                        
            for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__counter','pegawai__divisi').filter(tgl_absen__range=(dari,sampai), pegawai__status_id=sid,pegawai__divisi__in=divisi).order_by('tgl_absen','pegawai__divisi__divisi'):
                            
                sket = ""
                
                hari = a.tgl_absen.strftime("%A")
                hari_ini = nama_hari(hari) 
                
                if str(a.pegawai.counter) == "None":
                    bagian = f'{a.pegawai.divisi.divisi}'
                if str(a.pegawai.counter) == "None":
                    bagian = f'{a.pegawai.divisi.divisi}'
                else:
                    bagian = f'{a.pegawai.divisi.divisi} - {a.pegawai.counter.counter}' 
                    
                if a.masuk is not None:
                    if a.jam_masuk is not None and a.masuk > a.jam_masuk:
                        msk = f"<span class='text-danger'>{a.masuk}</span>"
                    else:
                        msk = f"{a.masuk}"
                else:
                    msk = '-'

                if a.pulang is not None:
                    plg = f"{a.pulang}"
                else:
                    plg = '-'

                if a.masuk_b is not None:
                    msk_b = f"{a.masuk_b}"
                else:
                    msk_b = '-'

                if a.pulang_b is not None:
                    plg_b = f"{a.pulang_b}"
                else:
                    plg_b = '-'

                if a.istirahat is not None and a.istirahat2 is not None:
                    ist = f'{a.istirahat} / {a.istirahat2}'
                elif a.istirahat is not None and a.istirahat2 is None:                  
                    ist = f'{a.istirahat}'
                elif a.istirahat is None and a.istirahat2 is not None:                  
                    ist = f'{a.istirahat2}'
                else:
                    ist = "-"    

                if a.istirahat_b is not None and a.istirahat2_b is not None:
                    ist_b = f" {a.istirahat_b} / {a.istirahat2_b})"
                elif a.istirahat_b is not None and a.istirahat2_b is None:
                    ist_b = f" {a.istirahat_b}"
                elif a.istirahat_b is None and a.istirahat2_b is not None:
                    ist_b = f" {a.istirahat2_b}"
                else:
                    ist_b = "-"


                if a.lama_istirahat is not None and a.istirahat is not None:
                    jkembali = datetime.combine(a.tgl_absen,a.istirahat) + timedelta(hours=float(a.lama_istirahat))
                else:
                    jkembali = None
                if a.kembali is not None and a.kembali2 is not None:
                    if jkembali is not None and a.kembali > jkembali.time():
                        kmb = f'<span class="text-danger">{a.kembali}</span> / {a.kembali2}'
                    else:
                        kmb = f'{a.kembali} / {a.kembali2}'
                elif a.kembali is not None and a.kembali2 is None:                  
                    if jkembali is not None and a.kembali > jkembali.time():
                        kmb = f'<span class="text-danger">{a.kembali}</span>'
                    else:
                        kmb = f'{a.kembali}'
                elif a.kembali is None and a.kembali2 is not None:                  
                    kmb = f'{a.kembali2}'    
                else:
                    kmb = "-"        

                if a.kembali_b is not None and a.kembali2_b is not None:
                    kmb_b = f" {a.kembali_b} / {a.kembali2_b})"
                elif a.kembali_b is not None and a.kembali2_b is None:
                    kmb_b = f" {a.kembali_b}"
                elif a.kembali_b is None and a.kembali2_b is not None:
                    kmb_b = f" {a.kembali2_b}"
                else:
                    kmb_b = "-" 
                

                if a.keterangan_absensi is not None:
                    sket += f'{a.keterangan_absensi}, '                 
                if a.keterangan_ijin is not None:
                    sket += f'{a.keterangan_ijin}, '
                    kijin = ''
                else:
                    if not r.session["ccabang"] in ['cihideung','sumedang']:
                        if a.masuk is not None and a.jam_masuk is not None:
                            if a.masuk > a.jam_masuk:
                                sket += f"Terlambat masuk tanpa ijin, "

                if a.keterangan_lain is not None:
                    sket += f'{a.keterangan_lain}, '                    
                if a.libur_nasional is not None:
                    sket += f'{a.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if a.istirahat is not None and a.lama_istirahat is not None:
                    jmkem = a.lama_istirahat
                else:
                    jmkem = None
                if sket == "":
                    sket = "-"
                absen = {
                    'id': a.id,
                    'tgl': datetime.strftime(a.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    "tgl_absen":a.tgl_absen,
                    'nama': a.pegawai.nama,
                    'nik': a.pegawai.nik,
                    'userid': a.pegawai.userid,
                    'bagian': bagian,
                    "jam_masuk":a.jam_masuk,
                    "jam_pulang":a.jam_pulang,
                    'masuk': msk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': plg,
                    'masuk_b': msk_b,
                    'keluar_b': ist_b,
                    'kembali_b': kmb_b,
                    'pulang_b': plg_b,
                    "jam_kembali":jmkem,
                    'tj': a.total_jam_kerja,
                    'ket': sket,
                    'sln': sln,
                    'ln': a.libur_nasional
                }

                data.append(absen)
        return JsonResponse({"data": data })


@authorization(["*"])
def cari_absensi_sid(r,dr, sp, sid):
    iduser = r.session['user']['id']
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
                
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).all().order_by('id')
        
        sid_lembur = 0
        
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
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
        
        return render(r,'hrd_app/absensi/cabsen.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def absensi_json(r, dr, sp, sid):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.session['user']['id']
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        # red = redis.Redis(host="15.63.254.114", port="6370", decode_responses=True, username="azril", password=132)
        today = datetime.today().date()
        # 
        # 
        
        # if red.hgetall(f"absensi-{dari.strftime('%Y-%m-%d')}-{sampai.strftime('%Y-%m-%d')}-{sid}"):
        #     return JsonResponse({"data": json.loads(red.hgetall(f"absensi-{dari.strftime('%Y-%m-%d')}-{sampai.strftime('%Y-%m-%d')}-{sid}")["data"]) })
        if int(sid) == 0:
            for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__counter','pegawai__divisi').filter(pegawai__divisi__in=divisi,tgl_absen__range=(dari,sampai)).order_by('tgl_absen','pegawai__divisi__divisi'):
                sket = ""
                hari = a.tgl_absen.strftime("%A")
                hari_ini = nama_hari(hari) 
                
                if str(a.pegawai.counter) == "None":
                    bagian = f'{a.pegawai.divisi.divisi}'
                else:
                    bagian = f'{a.pegawai.divisi.divisi} - {a.pegawai.counter.counter}' 
                    
                if a.masuk is not None:
                    if a.jam_masuk is not None and a.masuk > a.jam_masuk:
                        msk = f"<span class='text-danger'>{a.masuk}</span>"
                    else:
                        msk = f"{a.masuk}"
                else:
                    msk = '-'

                if a.pulang is not None:
                    plg = f"{a.pulang}"
                else:
                    plg = '-'

                if a.masuk_b is not None:
                    msk_b = f"{a.masuk_b}"
                else:
                    msk_b = '-'

                if a.pulang_b is not None:
                    plg_b = f"{a.pulang_b}"
                else:
                    plg_b = '-'

                if a.istirahat is not None and a.istirahat2 is not None:
                    ist = f'{a.istirahat} / {a.istirahat2}'
                elif a.istirahat is not None and a.istirahat2 is None:                  
                    ist = f'{a.istirahat}'
                elif a.istirahat is None and a.istirahat2 is not None:                  
                    ist = f'{a.istirahat2}'
                else:
                    ist = "-"    

                if a.istirahat_b is not None and a.istirahat2_b is not None:
                    ist_b = f" {a.istirahat_b} / {a.istirahat2_b})"
                elif a.istirahat_b is not None and a.istirahat2_b is None:
                    ist_b = f" {a.istirahat_b}"
                elif a.istirahat_b is None and a.istirahat2_b is not None:
                    ist_b = f" {a.istirahat2_b}"
                else:
                    ist_b = "-"


                if a.lama_istirahat is not None and a.istirahat is not None:
                    jkembali = datetime.combine(a.tgl_absen,a.istirahat) + timedelta(hours=float(a.lama_istirahat))
                else:
                    jkembali = None
                if a.kembali is not None and a.kembali2 is not None:
                    if jkembali is not None and a.kembali > jkembali.time():
                        kmb = f'<span class="text-danger">{a.kembali}</span> / {a.kembali2}'
                    else:
                        kmb = f'{a.kembali} / {a.kembali2}'
                elif a.kembali is not None and a.kembali2 is None:                  
                    if jkembali is not None and a.kembali > jkembali.time():
                        kmb = f'<span class="text-danger">{a.kembali}</span>'
                    else:
                        kmb = f'{a.kembali}'
                elif a.kembali is None and a.kembali2 is not None:                  
                    kmb = f'{a.kembali2}'    
                else:
                    kmb = "-"        

                if a.kembali_b is not None and a.kembali2_b is not None:
                    kmb_b = f" {a.kembali_b} / {a.kembali2_b})"
                elif a.kembali_b is not None and a.kembali2_b is None:
                    kmb_b = f" {a.kembali_b}"
                elif a.kembali_b is None and a.kembali2_b is not None:
                    kmb_b = f" {a.kembali2_b}"
                else:
                    kmb_b = "-" 
                

                if a.keterangan_absensi is not None:
                    sket += f'{a.keterangan_absensi}, '                 
                if a.keterangan_ijin is not None:
                    sket += f'{a.keterangan_ijin}, '
                    kijin = ''
                else:
                    if not r.session["ccabang"] in ['cihideung','sumedang']:
                        if a.masuk is not None and a.jam_masuk is not None:
                            if a.masuk > a.jam_masuk:
                                sket += f"Terlambat masuk tanpa ijin, "
                if a.keterangan_lain is not None:
                    sket += f'{a.keterangan_lain}, '                    
                if a.libur_nasional is not None:
                    sket += f'{a.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if a.istirahat is not None and a.lama_istirahat is not None:
                    jmkem = a.lama_istirahat
                else:
                    jmkem = None
                if sket == "":
                    sket = "-"
                absen = {
                    'id': str(a.id),
                    'tgl': str(datetime.strftime(a.tgl_absen,'%d-%m-%Y')),
                    'hari': hari_ini,
                    "tgl_absen":str(a.tgl_absen),
                    'nama': str(a.pegawai.nama),
                    'nik': str(a.pegawai.nik),
                    'userid': str(a.pegawai.userid),
                    'bagian': str(bagian),
                    "jam_masuk":str(a.jam_masuk),
                    "jam_pulang":str(a.jam_pulang),
                    'masuk': str(msk),
                    'keluar': str(ist),
                    'kembali': str(kmb),
                    'pulang': str(plg),
                    'masuk_b': str(msk_b),
                    'keluar_b': str(ist_b),
                    'kembali_b': str(kmb_b),
                    'pulang_b': str(plg_b),
                    "jam_kembali":str(jmkem),
                    'tj': str(a.total_jam_kerja),
                    'ket': str(sket),
                    'sln': str(sln),
                    'ln': str(a.libur_nasional)
                }

                data.append(absen)
            
        else:                        
            for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__counter','pegawai__divisi').filter(pegawai__divisi__in=divisi,tgl_absen__range=(dari,sampai), pegawai__status_id=sid).order_by('tgl_absen','pegawai__divisi__divisi'):
                            
                sket = ""
                
                hari = a.tgl_absen.strftime("%A")
                hari_ini = nama_hari(hari) 
                
                if str(a.pegawai.counter) == "None":
                    bagian = f'{a.pegawai.divisi.divisi}'
                else:
                    bagian = f'{a.pegawai.divisi.divisi} - {a.pegawai.counter.counter}' 
                if a.masuk is not None:
                    if a.jam_masuk is not None and a.masuk > a.jam_masuk:
                        msk = f"<span class='text-danger'>{a.masuk}</span>"
                    else:
                        msk = f"{a.masuk}"
                else:
                    msk = '-'

                if a.pulang is not None:
                    plg = f"{a.pulang}"
                else:
                    plg = '-'

                if a.masuk_b is not None:
                    msk_b = f"{a.masuk_b}"
                else:
                    msk_b = '-'

                if a.pulang_b is not None:
                    plg_b = f"{a.pulang_b}"
                else:
                    plg_b = '-'

                if a.istirahat is not None and a.istirahat2 is not None:
                    ist = f'{a.istirahat} / {a.istirahat2}'
                elif a.istirahat is not None and a.istirahat2 is None:                  
                    ist = f'{a.istirahat}'
                elif a.istirahat is None and a.istirahat2 is not None:                  
                    ist = f'{a.istirahat2}'
                else:
                    ist = "-"    

                if a.istirahat_b is not None and a.istirahat2_b is not None:
                    ist_b = f" {a.istirahat_b} / {a.istirahat2_b}"
                elif a.istirahat_b is not None and a.istirahat2_b is None:
                    ist_b = f" {a.istirahat_b}"
                elif a.istirahat_b is None and a.istirahat2_b is not None:
                    ist_b = f" {a.istirahat2_b}"
                else:
                    ist_b = "-"
            
                    
                if a.lama_istirahat is not None and a.istirahat is not None:
                    jkembali = datetime.combine(a.tgl_absen,a.istirahat) + timedelta(hours=float(a.lama_istirahat))
                else:
                    jkembali = None
                if a.kembali is not None and a.kembali2 is not None:
                    if jkembali is not None and a.kembali > jkembali.time():
                        kmb = f'<span class="text-danger">{a.kembali}</span> / {a.kembali2}'
                    else:
                        kmb = f'{a.kembali} / {a.kembali2}'
                elif a.kembali is not None and a.kembali2 is None:                  
                    if jkembali is not None and a.kembali > jkembali.time():
                        kmb = f'<span class="text-danger">{a.kembali}</span>'
                    else:
                        kmb = f'{a.kembali}'
                elif a.kembali is None and a.kembali2 is not None:                  
                    kmb = f'{a.kembali2}'    
                else:
                    kmb = "-"        

                if a.kembali_b is not None and a.kembali2_b is not None:
                    kmb_b = f" {a.kembali_b} / {a.kembali2_b}"
                elif a.kembali_b is not None and a.kembali2_b is None:
                    kmb_b = f" {a.kembali_b}"
                elif a.kembali_b is None and a.kembali2_b is not None:
                    kmb_b = f" {a.kembali2_b}"
                else:
                    kmb_b = "-" 
                

                if a.keterangan_absensi is not None:
                    sket += f'{a.keterangan_absensi}, '                 
                if a.keterangan_ijin is not None:
                    sket += f'{a.keterangan_ijin}, '
                    kijin = '' 
                else: 
                    if not r.session["ccabang"] in ['cihideung','sumedang']:
                        if a.masuk is not None and a.jam_masuk is not None:
                            if a.masuk > a.jam_masuk:
                                sket += f"Terlambat masuk tanpa ijin, "

                if a.keterangan_lain is not None:
                    sket += f'{a.keterangan_lain}, '                    
                if a.libur_nasional is not None:
                    sket += f'{a.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if a.istirahat is not None and a.lama_istirahat is not None:
                    jmkem = a.lama_istirahat
                else:
                    jmkem = None
                if sket == "":
                    sket = "-"
                absen = {
                    'id': str(a.id),
                    'tgl': str(datetime.strftime(a.tgl_absen,'%d-%m-%Y')),
                    'hari': hari_ini,
                    "tgl_absen":str(a.tgl_absen),
                    'nama': str(a.pegawai.nama),
                    'nik': str(a.pegawai.nik),
                    'userid': str(a.pegawai.userid),
                    'bagian': str(bagian),
                    "jam_masuk":str(a.jam_masuk),
                    "jam_pulang":str(a.jam_pulang),
                    'masuk': str(msk),
                    'keluar': str(ist),
                    'kembali': str(kmb),
                    'pulang': str(plg),
                    'masuk_b': str(msk_b),
                    'keluar_b': str(ist_b),
                    'kembali_b': str(kmb_b),
                    'pulang_b': str(plg_b),
                    "jam_kembali":str(jmkem),
                    'tj': str(a.total_jam_kerja),
                    'ket': str(sket),
                    'sln': str(sln),
                    'ln': str(a.libur_nasional)
                }

                data.append(absen)
        return JsonResponse({"data": data })


# @jit(nopython=True)
@authorization(["*"])
def pabsen(req):    
    try:
        print(datetime.now())
        startglobal = time.perf_counter()
        t1 = req.POST.get('tgl1')
        t2 = req.POST.get('tgl2')
        sid = req.POST.get('sid')
        # today = date.today()
        # tdy = datetime.strftime(today, "%d-%m-%Y")
        if t1 != "" and t2 != "":     
            dari = datetime.strptime(f'{t1} 00:00:00', "%d-%m-%Y %H:%M:%S")
            sampai = datetime.strptime(f'{t2} 23:59:59', "%d-%m-%Y %H:%M:%S")
            
            dr = datetime.strftime(dari, "%d-%m-%Y")
            sp = datetime.strftime(sampai, "%d-%m-%Y")
            # if dr == sp and dr == tdy and sp == tdy:
            #     tminus1 = date.today() + timedelta(days=-1)
            #     tplus1 = date.today()
            #     dari = datetime.strptime(f'{tminus1} 00:00:00', "%Y-%m-%d %H:%M:%S")
            #     sampai = datetime.strptime(f'{tplus1} 23:59:59', "%Y-%m-%d %H:%M:%S")    
            #     dr = datetime.strftime(dari, "%d-%m-%Y")
            #     sp = datetime.strftime(sampai, "%d-%m-%Y")
        else:
            tminus1 = date.today() + timedelta(days=-1)
            tplus1 = date.today()
            dari = datetime.strptime(f'{tminus1} 00:00:00', "%Y-%m-%d %H:%M:%S")
            sampai = datetime.strptime(f'{tplus1} 23:59:59', "%Y-%m-%d %H:%M:%S")    
            dr = datetime.strftime(dari, "%d-%m-%Y")
            sp = datetime.strftime(sampai, "%d-%m-%Y")
        rangetgl = pd.date_range(dari, sampai).tolist()
        pegawai = [] 
        luserid = []  
        
        # buat tabel absen
        id_user = req.session['user']['id']
        aksesdivisi = akses_divisi_db.objects.using(req.session["ccabang"]).filter(user_id=id_user)
        userp = akses_db.objects.select_related("pegawai").using(req.session["ccabang"]).filter(user_id=id_user)
        if not userp.exists():
            return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses"},status=400)
        divisi = [div.divisi for div in aksesdivisi]
        pegawaiLoop = pegawai_db.objects.using(req.session["ccabang"]).select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(divisi__in=divisi).values("jabatan__jabatan","counter__counter","divisi__divisi","kelompok_kerja__kelompok","hari_off__hari","hari_off2__hari","nama","gender","userid","id","status__status","status_id","sisa_cuti","shift","nik","shift")
        # try:
        insertab = []
        if int(sid) == 0:
            for p in pegawaiLoop:
                jabatan = p["jabatan__jabatan"] if p["jabatan__jabatan"] is not None else None
                counter = p["counter__counter"] if p["counter__counter"] is not None else None
                divisi = p["divisi__divisi"] if p["divisi__divisi"] is not None else None
                kelompok_kerja = p["kelompok_kerja__kelompok"] if p["kelompok_kerja__kelompok"] is not None else None
                ho = p["hari_off2__hari"] if p["hari_off2__hari"] is not None else None
                data = {
                    'idp' : p["id"],
                    'nama' : p["nama"],
                    'userid' : p["userid"],
                    'gender' : p["gender"],
                    'status' : p["status__status"],
                    'status_id' : p["status_id"],
                    'nik' : p["nik"],
                    'divisi' : divisi,
                    'jabatan' : jabatan,                
                    'hari_off' : p["hari_off__hari"],
                    'hari_off2' : ho,
                    'kelompok_kerja' : kelompok_kerja,
                    'sisa_cuti' : p["sisa_cuti"],
                    'shift' : p["shift"],
                    'counter' : counter
                }
                pegawai.append(data)        
                luserid.append(p["userid"])
                for tgl in rangetgl + [(sampai + timedelta(days=1))]:
                    if absensi_db.objects.using(req.session["ccabang"]).filter(pegawai_id=p["id"],tgl_absen=tgl.date()).exists():
                        pass
                    else:
                        insertab.append(absensi_db(tgl_absen=tgl.date(),pegawai_id=p["id"]))
        else:
            for p in [pgw for pgw in pegawaiLoop if pgw["status_id"] == int(sid)]:
                jabatan = p["jabatan__jabatan"] if p["jabatan__jabatan"] is not None else None
                counter = p["counter__counter"] if p["counter__counter"] is not None else None
                divisi = p["divisi__divisi"] if p["divisi__divisi"] is not None else None
                kelompok_kerja = p["kelompok_kerja__kelompok"] if p["kelompok_kerja__kelompok"] is not None else None
                ho = p["hari_off2__hari"] if p["hari_off2__hari"] is not None else None
                data = {
                    'idp' : p["id"],
                    'nama' : p["nama"],
                    'userid' : p["userid"],
                    'gender' : p["gender"],
                    'status' : p["status__status"],
                    'status_id' : p["status_id"],
                    'nik' : p["nik"],
                    'divisi' : divisi,
                    'jabatan' : jabatan,                
                    'hari_off' : p["hari_off__hari"],
                    'hari_off2' : ho,   
                    'kelompok_kerja' : kelompok_kerja,
                    'sisa_cuti' : p["sisa_cuti"],
                    'shift' : p["shift"],
                    'counter' : counter
                }
                pegawai.append(data)        
                luserid.append(p["userid"])
                for tgl in [(dari - timedelta(days=1))] + rangetgl + [(sampai + timedelta(days=1))]:
                    if absensi_db.objects.using(req.session["ccabang"]).filter(pegawai_id=p["id"],tgl_absen=tgl.date()).exists():
                        pass
                    else:
                        insertab.append(absensi_db(tgl_absen=tgl.date(),pegawai_id=p["id"]))   
        absensi_db.objects.using(req.session["ccabang"]).bulk_create(insertab)
        dmesin = []
        try:
            for m in mesin_db.objects.using(req.session["ccabang"]).filter(status="Active"):
                ip = m.ipaddress
                # conn = None
                zk = ZK(str(ip), port=4370, timeout=65)
                conn = zk.connect()
                conn.disable_device()
                # dt absensi
                absensi = conn.get_attendance()
                [dmesin.append({"userid":a.user_id,"jam_absen":datetime.strftime(a.timestamp,"%Y-%m-%d %H:%M:%S"),"punch": a.punch,"mesin":m.nama}) for a in absensi if dari <= a.timestamp <= sampai and str(a.user_id) in luserid]
                conn.enable_device()
                conn.disconnect()
        except Exception as e:
            print(e)
            messages.error(req,e)
            return redirect("absensi_tgl",sid=sid,dr=dr,sp=sp)

        # with open("data.json") as f:
        #     dmesin = json.loads(f.read())
        att = sorted(dmesin, key=lambda i: i['jam_absen'])
        # print(att)
        ddr = []
        for d in data_raw_db.objects.using(req.session["ccabang"]).filter(userid__in=luserid,jam_absen__range=(dari - timedelta(days=1),sampai + timedelta(days=1))):
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
        for d2 in data_trans_db.objects.using(req.session["ccabang"]).filter(userid__in=luserid,jam_absen__range=(dari - timedelta(days=1),sampai + timedelta(days=1))):
            data = {
                "userid": d2.userid,
                "jam_absen": d2.jam_absen,
                "punch": d2.punch,
                "mesin": d2.mesin,
                "ket": d2.keterangan
            }
            ddtor.append(data)
            ddt.append(data)
            
        status_lh = [st.status_pegawai.pk for st in status_pegawai_lintas_hari_db.objects.using(req.session["ccabang"]).all()]
        # # proses data simpan di dt array
        # # obj 
        jamkerja = jamkerja_db.objects.using(req.session["ccabang"]).select_related("shift").all().values("id","kk_id","jam_masuk","jam_pulang",'lama_istirahat',"hari","shift__shift")
        absensi =  absensi_db.objects.using(req.session["ccabang"]).select_related("pegawai","pegawai__divisi").filter(tgl_absen__range=[(dari - timedelta(days=1)),(sampai + timedelta(days=1))],pegawai__userid__in=luserid).order_by("tgl_absen").values("id","pegawai_id","pegawai__userid","pegawai__kelompok_kerja_id","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","jam_masuk","jam_pulang","lama_istirahat","shift")
        if req.session["ccabang"] != "tasik":
            prosesabsensi.lh(att,luserid,ddr,rangetgl,pegawai,jamkerja,status_lh,req.session["ccabang"],ddt,ddtor,absensi)
        else:
            prosesabsensi.nlh(att,luserid,ddr,rangetgl,pegawai,jamkerja,status_lh,req.session["ccabang"],ddt,ddtor,absensi)    
        print("SELESAI")

        startsec = time.perf_counter()
        ijin = []  
        libur = []
        cuti = []
        geser = []
        geserdr = []
        kompen = []
        opg = []
        opgdr = []
        dl = []
        dl_idp = []
        ijindl = []
        lsopg = []
        
        # list status pegawai yang dapat opg
        for s in list_pegawai_opg_db.objects.using(req.session["ccabang"]).all():
            lsopg.append(s.pegawai_id)

        # data ijin
        for i in ijin_db.objects.using(req.session["ccabang"]).select_related('ijin','pegawai').filter(tgl_ijin__range=(dari.date(),sampai.date())).values("ijin__jenis_ijin","tgl_ijin","pegawai_id","keterangan"):
            data = {
                "ijin" : i["ijin__jenis_ijin"],
                "tgl_ijin" : i["tgl_ijin"],
                "idp" : i["pegawai_id"],
                "keterangan" : i["keterangan"]
            }
            ijin.append(data)
        
        # data libur nasional
        for l in libur_nasional_db.objects.using(req.session["ccabang"]).filter(tgl_libur__range=(dari.date(),sampai.date())).values("libur","tgl_libur","insentif_karyawan","insentif_staff"):
            data = {
                'libur' : l["libur"],
                'tgl_libur' : l["tgl_libur"],
                'insentif_karyawan' : l["insentif_karyawan"],
                'insentif_staff' : l["insentif_staff"]
            }    
            libur.append(data)  
            
        # data cuti
        for c in cuti_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(tgl_cuti__range=(dari.date(),sampai.date())).values("id","pegawai_id","tgl_cuti","keterangan"):
            data = {
                'id': c["id"],
                'idp' : c["pegawai_id"],
                'tgl_cuti' : c["tgl_cuti"],
                'keterangan' : c["keterangan"]
            }                
            cuti.append(data)
            
        # data geser off
        for g in geseroff_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(ke_tgl__range=(dari.date(),sampai.date())).values("id","pegawai_id","dari_tgl","ke_tgl","keterangan"):
            data = {
                'id' : g["id"],
                'idp' : g["pegawai_id"], 
                'dari_tgl' : g["dari_tgl"],
                'ke_tgl' : g["ke_tgl"],
                'keterangan' : g["keterangan"]
            } 
            geser.append(data)
        for g in geseroff_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(dari_tgl__range=(dari.date(),sampai.date())).values("id","pegawai_id","dari_tgl","ke_tgl","keterangan"):
            data = {
                'id' : g["id"],
                'idp' : g["pegawai_id"], 
                'dari_tgl' : g["dari_tgl"],
                'ke_tgl' : g["ke_tgl"],
                'keterangan' : g["keterangan"]
            } 
            geserdr.append(data)
        status_ln = [st.pegawai_id for st in list_pegawai_opg_libur_nasional_db.objects.using(req.session["ccabang"]).all()]
        # data opg
        for o in opg_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(diambil_tgl__range=(dari.date(),sampai.date())).values("id","pegawai_id","opg_tgl","diambil_tgl","keterangan","status","edit_by"):
            data = {
                'id':o["id"],
                'idp': o["pegawai_id"],
                'opg_tgl':o["opg_tgl"],
                'diambil_tgl':o["diambil_tgl"],
                'keterangan':o["keterangan"],
                "status":o["status"],
                "edit_by":o["edit_by"]
            }
            opg.append(data)
        for odr in opg_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(opg_tgl__range=(dari.date(),sampai.date())).values("id","pegawai_id","opg_tgl","diambil_tgl","keterangan","status","edit_by"):
            data = {
                'id':odr["id"],
                'idp': odr["pegawai_id"],
                'opg_tgl':odr["opg_tgl"],
                'diambil_tgl':odr["diambil_tgl"],
                'keterangan':odr["keterangan"],
                "status":odr["status"],
                "edit_by":odr["edit_by"]
            }
            opgdr.append(data)
        
        # data dinas luar
        for n in dinas_luar_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(tgl_dinas__range=(dari.date(),sampai.date())).values("pegawai_id","tgl_dinas","keterangan"):
            data = {
                'idp': n["pegawai_id"],
                'tgl_dinas':n["tgl_dinas"],
                'keterangan':n["keterangan"]
            }
            dl.append(data)
            dl_idp.append(n.pegawai_id)
        for ij in ijin_db.objects.using(req.session["ccabang"]).filter(tgl_ijin__range=(dari.date(),sampai.date())).values("tgl_ijin","pegawai_id","ijin_id","ijin__jenis_ijin"):
            if re.search('(dinas luar|dl)',ij["ijin__jenis_ijin"],re.IGNORECASE) is not None:
                data = {
                    "tgl":ij["tgl_ijin"],
                    "idp":ij["pegawai_id"],
                    "ijin":ij["ijin_id"]
                }
                ijindl.append(data)
        for k in kompen_db.objects.using(req.session["ccabang"]).all().values("id","pegawai_id","jenis_kompen","kompen","tgl_kompen"):
            data = {
                "idl":k["id"],
                "idp":k["pegawai_id"],
                "jenis_kompen":k["jenis_kompen"],
                "kompen":k["kompen"],
                "tgl_kompen":k["tgl_kompen"],
            }
            kompen.append(data)
            
        # data absensi
        if int(sid) == 0:
            data = absensi_db.objects.using(req.session["ccabang"]).select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen__range=(dari.date(),sampai.date())).values("id","pegawai_id","pegawai__userid","pegawai__kelompok_kerja_id","pegawai__hari_off__hari","pegawai__hari_off2__hari","pegawai__status_id","pegawai__status__status","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift")
        elif int(sid) > 0:
            data = absensi_db.objects.using(req.session["ccabang"]).select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen__range=(dari.date(),sampai.date()),pegawai__status_id=sid).values("id","pegawai_id","pegawai__userid","pegawai__kelompok_kerja_id","pegawai__hari_off__hari","pegawai__hari_off2__hari","pegawai__status_id","pegawai__status__status","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift")
        insertopg = []
        insertijin  = []
        username = req.session["user"]["nama"]
        cabang = req.session["ccabang"]
        for a in data:
            day = a["tgl_absen"].strftime("%A")
            nh = nama_hari(day)  
            """ Rules OPG (staff & karyawan) & Insentif (hanya untuk karyawan) :
            
            Staff :
            --> jika ada libur nasional dan jatuh di hari biasa (senin - sabtu), maka staff yang memiliki off reguler bertepatan
            dengan libur nasional tersebut akan mendapat opg = 2 jika masuk (off pengganti reguler dan off pengganti tgl merah), 
            jika tidak masuk mendapat opg = 1 (off pengganti reguler)
            
            --> jika ada libur nasional dan jatuh di hari minggu, maka staff yang memiliki off reguler bertepatan dengan libur
            nasional tersebut jika masuk mendapat opg = 1 (off pengganti reguler)
            
            --> jika tidak ada libur nasional, maka staff yang masuk di hari off regulernya maka mendapat opg = 1 (off pengganti 
            reguler)2
            
            Karyawan + SPG dibayar oleh Asia:
        geser = []
        geserdr = []
        kompen = []
        opg = []
        opgdr = []
        dl = []
        dl_idp = []
            """  
            # OFF & OFF Pengganti Reguler
            # jika ada absen masuk dan pulang
            # rencana cronjob jalan
            if (a["masuk"] is not None and a["pulang"] is not None) or (a["masuk_b"] is not None and a["pulang_b"] is not None):
                if nh in [str(a["pegawai__hari_off__hari"]),str(a["pegawai__hari_off2__hari"])]:
                    if a["pegawai_id"] in lsopg and re.search("security",a["pegawai__status__status"],re.IGNORECASE) is None and next((False for gs in geserdr if gs["idp"] == a["pegawai_id"] and gs["dari_tgl"] == a["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == a["pegawai_id"] and o["opg_tgl"] == a["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                        opgdr.append({
                            'id':0,
                            'idp':a["pegawai_id"],
                            'opg_tgl':a["tgl_absen"],
                            'diambil_tgl':"",
                            'keterangan':"OFF Pengganti Reguler"
                        })
                        insertopg.append(opg_db(pegawai_id=a["pegawai_id"],opg_tgl=a["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                    else:
                        pass
                else: 
                    if str(a["pegawai__hari_off__hari"]) == "On Off":
                        a["keterangan_absensi"] = None
                            
            # jika tidak ada masuk dan pulang   
            else:
                # jika dinas luar
                if str(a["pegawai__hari_off__hari"]) == 'On Off':
                    a["keterangan_absensi"] = 'OFF'
                for il in ijindl:
                    if il["tgl"] == a["tgl_absen"] and int(il["idp"]) == int(a["pegawai_id"]) and nh in [str(a["pegawai__hari_off__hari"]),str(a["pegawai__hari_off2__hari"])] and  a["pegawai_id"] in lsopg and next((False for gs in geserdr if gs["idp"] == a["pegawai_id"] and gs["dari_tgl"] == a["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == a["pegawai_id"] and o["opg_tgl"] == a["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                        opgdr.append({
                            'id':0,
                            'idp':a["pegawai_id"],
                            'opg_tgl':a["tgl_absen"],
                            'diambil_tgl':"",
                            'keterangan':"OFF Pengganti Reguler"
                        })
                        insertopg.append(opg_db(pegawai_id=a["pegawai_id"],opg_tgl=a["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                    else:
                        pass
                # jika dia hari ini off
                if (a["masuk"] is not None or a["pulang"] is not None) or (a["masuk_b"] is not None or a["pulang_b"] is not None):
                    if str(a["pegawai__hari_off__hari"]) == "On Off":
                        a["keterangan_absensi"] = None
                else:
                    if str(a["pegawai__hari_off__hari"]) == str(nh):
                        a["keterangan_absensi"] = 'OFF'
                    elif str(a["pegawai__hari_off__hari"]) == 'On Off':
                        a["keterangan_absensi"] = 'OFF'
                    if str(a["pegawai__hari_off2__hari"]) == str(nh):
                        a["keterangan_absensi"] = 'OFF'
                    else:
                        pass   
                # jika hari ini dia adalah off nya
            
            # libur nasional
            for l in libur:
            # jika ada absen di hari libutart = time.perf_counter()r nasional
                a["libur_nasional"] = None
                if a["pegawai_id"] in lsopg and l['tgl_libur'] == a["tgl_absen"]:                            
                    a["libur_nasional"] = l['libur']
                    
                    # Hari Minggu
                    if str(nh) == 'Minggu':                        
                            # Staff
                        if a["pegawai_id"] in status_ln: # regex
                            # jika hari off nya adalah hari minggu dan masuk maka hanya akan mendapatkan 1 opg
                            if str(nh) in [str(a["pegawai__hari_off__hari"]), str(a["pegawai__hari_off2__hari"])] and (a["masuk"] is not None and a["pulang"] is not None) or (a["masuk_b"] is not None and a["pulang_b"] is not None) and next((False for gs in geserdr if gs["idp"] == a["pegawai_id"] and gs["dari_tgl"] == a["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == a["pegawai_id"] and o["opg_tgl"] == a["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                                opgdr.append({
                                    'id':0,
                                    'idp':a["pegawai_id"],
                                    'opg_tgl':a["tgl_absen"],
                                    'diambil_tgl':"",
                                    'keterangan':"OFF Pengganti Reguler"
                                })
                                insertopg.append(opg_db(pegawai_id=a["pegawai_id"],opg_tgl=a["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                            else:
                                pass                        
                        # Karyawan
                        else:
                            pass         
                    
                    # Bukan Hari Minggu
                    else:                                                        
                        # Staff
                        if a["pegawai_id"] in status_ln:
                            if str(nh) in [str(a["pegawai__hari_off__hari"]), str(a["pegawai__hari_off2__hari"])]:
                                # JIKA DIA MASUK DIHARI MERAH DILIBUR REGULERNYA MAKA AKAN DAPAT 2 OPG
                                if (a["masuk"] is not None and a["pulang"] is not None) or (a["masuk_b"] is not None and a["pulang_b"] is not None):
                                    if next((False for gs in geserdr if gs["idp"] == a["pegawai_id"] and gs["dari_tgl"] == a["tgl_absen"]),True):
                                        if next((False for o in opgdr if o["idp"] == a["pegawai_id"] and o["opg_tgl"] == a["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                                            opgdr.append({
                                                'id':0,
                                                'idp':a["pegawai_id"],
                                                'opg_tgl':a["tgl_absen"],
                                                'diambil_tgl':"",
                                                'keterangan':"OFF Pengganti Reguler"
                                            })
                                            insertopg.append(opg_db(pegawai_id=a["pegawai_id"],opg_tgl=a["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                                            
                                        if next((False for o in opgdr if o["idp"] == a["pegawai_id"] and o["opg_tgl"] == a["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                            opgdr.append({
                                                'id':0,
                                                'idp':a["pegawai_id"],
                                                'opg_tgl':a["tgl_absen"],
                                                'diambil_tgl':"",
                                                'keterangan':"OFF Pengganti Tgl Merah"
                                            })
                                            insertopg.append(opg_db(pegawai_id=a["pegawai_id"],opg_tgl=a["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                                # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                                else:
                                    if next((False for o in opgdr if o["idp"] == a["pegawai_id"] and o["opg_tgl"] == a["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                        opgdr.append({
                                            'id':0,
                                            'idp':a["pegawai_id"],
                                            'opg_tgl':a["tgl_absen"],
                                            'diambil_tgl':"",
                                            'keterangan':"OFF Pengganti Tgl Merah"
                                        })
                                        insertopg.append(opg_db(pegawai_id=a["pegawai_id"],opg_tgl=a["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                            # JIKA HARI OFF TIDAK BERTEPATAN HARI LIBUR NASIONAL
                            else:
                                if (a["masuk"] is not None and a["pulang"] is not None) or (a["masuk_b"] is not None and a["pulang_b"] is not None):
                                    if next((False for gs in geserdr if gs["idp"] == a["pegawai_id"] and gs["dari_tgl"] == a["tgl_absen"]),True):
                                        if next((False for o in opgdr if o["idp"] == a["pegawai_id"] and o["opg_tgl"] == a["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                            opgdr.append({
                                                'id':0,
                                                'idp':a["pegawai_id"],
                                                'opg_tgl':a["tgl_absen"],
                                                'diambil_tgl':"",
                                                'keterangan':"OFF Pengganti Tgl Merah"
                                            })
                                            insertopg.append(opg_db(pegawai_id=a["pegawai_id"],opg_tgl=a["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                                # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                                else:
                                    pass
                        
                        # Karyawan
                        # JIKA MASUK HANYA MENDAPATKAN 1 OPG DAN INSENTIF
                        else:
                            if (a["masuk"] is not None and a["pulang"] is not None) or (a["masuk_b"] is not None and a["pulang_b"] is not None) and next((False for gs in geserdr if gs["idp"] == a["pegawai_id"] and gs["dari_tgl"] == a["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == a["pegawai_id"] and o["opg_tgl"] == a["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):                                        
                                    a["insentif"] = l['insentif_karyawan']
                            else:
                                pass    
                        
            # ijin
            for i in ijin:
                if a["pegawai_id"] == i['idp'] and i['tgl_ijin'] == a["tgl_absen"]:
                    ij = i['ijin']
                    ket = i['keterangan']
                    a["keterangan_ijin"] = f'{ij}-({ket})'
                else:
                    pass                                 
            
            for kmpn in kompen:
                if a["pegawai_id"] == kmpn["idp"] and kmpn["tgl_kompen"] == a["tgl_absen"]:
                    if a["jam_masuk"] is not None and a["jam_pulang"] is None and a["masuk"] is not None and a["pulang"] is not None:
                        if a["pulang"] > a["masuk"]:
                            jm = datetime.combine(a["tgl_absen"],a["jam_masuk"])
                            jp = datetime.combine(a["tgl_absen"],a["jam_pulang"])
                            
                            jkompen = float(kmpn["kompen"])
                            
                            if kmpn["jenis_kompen"] == 'awal':
                                njm = jm - timedelta(hours=jkompen)
                                njp = a["jam_pulang"]
                            elif kmpn["jenis_kompen"] == 'akhir':    
                                njm = a["jam_masuk"]
                                njp = jp + timedelta(hours=jkompen)
                            else:    
                                njm = jm - timedelta(hours=jkompen)
                                njp = jp + timedelta(hours=jkompen)
                            
                            dmsk = f'{a["tgl_absen"]} {a["masuk"]}'
                            dplg = f'{a["tgl_absen"]} {a["pulang"]}'
                            
                            msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                            plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                            
                            dselisih = plg - msk
                            djam_selisih = f'{a["tgl_absen"]} {dselisih}'
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
                            a["jam_masuk"] = njm
                            a["jam_pulang"] = njp
                        else: 
                            tjk = 0   
                    else:
                        tjk = 0
                    if kmpn["jenis_kompen"] == 'awal':
                        a["keterangan_lain"] = f"Kompen/PJK-Awal {kmpn['kompen']} Jam"
                    elif kmpn["jenis_kompen"] == "akhir":
                        a["keterangan_lain"] = f"Kompen/PJK-Akhir {kmpn['kompen']} Jam"
                    else:
                        a["keterangan_lain"] = f"Kompen/PJK 1 hari"
                    nama_user = username
                    a["total_jam_kerja"] = round(tjk,1)
                    a["edit_by"] = nama_user
                else:
                    pass
            
            # cuti
            for c in cuti:
                # jika didalam data cuti ada pegawai id
                if a["pegawai_id"] == c['idp'] and c['tgl_cuti'] == a["tgl_absen"]:
                    # jika tidak masuk dan pulang
                    if a["masuk"] is not None and a["pulang"] is not None:
                        dmsk = f'{a["tgl_absen"]} {a["masuk"]}'
                        dplg = f'{a["tgl_absen"]} {a["pulang"]}'
                        
                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                        
                        dselisih = plg - msk
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
                        # jika jam kerja kurang dari 4 jam
                        if int(selisih.hour) <= 4:
                            a["keterangan_absensi"] = c['keterangan']
                        # jika jam kerja lebih dari 4 jam
                        else:
                            cuti_db.objects.using(cabang).get(id=int(c['id'])).delete()
                            pg = pegawai_db.objects.using(cabang).get(pk=a["pegawai_id"])
                            sc = pg.sisa_cuti
                            a["keterangan_absensi"] = ""
                            pg.sisa_cuti = sc + 1
                            pg.save(using=cabang)          
                    else:
                        a["keterangan_absensi"] = c['keterangan']
                else:
                    pass        
                
            # geser off
            for g in geser:
                if a["pegawai_id"] == g['idp']:
                    if g['ke_tgl'] == a["tgl_absen"]:
                        # jika ada geser off dan dia tidak masuk
                        if a["masuk"] is None and a["pulang"] is None:
                            drt = datetime.strftime(g['dari_tgl'], '%d-%m-%Y')
                            a["keterangan_absensi"] = f'Geser OFF-({drt})' 
                        # jika ada geser off dan dia masuk
                        else:
                            geseroff_db.objects.using(cabang).get(id=int(g['id'])).delete()    
                    elif g["dari_tgl"] == a["tgl_absen"]:
                        if a["masuk"] is not None and a["pulang"] is not None:
                            a["keterangan_absensi"] = None
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            # opg
            for o in opg:
                if a["pegawai_id"] == o['idp'] and o['diambil_tgl'] == a["tgl_absen"]:
                    opg_detail = opg_db.objects.using(cabang).get(pk=int(o["id"]))
                    # jika tidak masuk dan tidak ada pulang
                    if a["masuk"] is None and a["pulang"] is None:
                        topg = datetime.strftime(o['opg_tgl'], '%d-%m-%Y')
                        a["keterangan_absensi"] = f'OPG-({topg})'
                        
                        opg_detail.status = 1
                        opg_detail.edit_by ='Program'
                        opg_detail.save(using=cabang)
                    # jika masuk dan pulang
                    else:
                        opg_detail.diambil_tgl = None
                        opg_detail.edit_by = 'Program'
                        opg_detail.save(using=cabang)
                else:
                    pass        
            
            # dinas luar   
            for n in dl:
                if a["pegawai_id"] == n['idp'] and n['tgl_dinas'] == a["tgl_absen"]:
                    ket = n['keterangan']
                    a["keterangan_absensi"] = f'Dinas Luar-({ket})'
                else:
                    pass    
                                    
            # total jam kerja         
            if a["masuk"] is not None and a["pulang"] is not None:
                if a["pulang"] > a["masuk"]:
                    
                    dmsk = f'{a["tgl_absen"]} {a["masuk"]}'
                    dplg = f'{a["tgl_absen"]} {a["pulang"]}'
                    
                    msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                    plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih = plg - msk
                    djam_selisih = f'{a["tgl_absen"]} {dselisih}'
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
                    
                    tplus = a["tgl_absen"]        
                    
                    dmsk = f'{a["tgl_absen"]} {a["masuk"]}'
                    dplg = f'{tplus} {a["pulang"]}'
                    
                    msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                    plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih = plg - msk
                    djam_selisih = f'{a["tgl_absen"]} {dselisih}'
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
            if a["masuk_b"] is not None and a["pulang_b"] is not None:
                if a["pulang_b"] > a["masuk_b"]:
                    
                    dmsk_b = f'{a["tgl_absen"]} {a["masuk_b"]}'
                    dplg_b = f'{a["tgl_absen"]} {a["pulang_b"]}'
                    
                    msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
                    plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_b = plg_b - msk_b
                    djam_selisih_b = f'{a["tgl_absen"]} {dselisih_b}'
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
                    
                    tplus_b = a["tgl_absen"]
                    dmsk_b = f'{a["tgl_absen"]} {a["masuk_b"]}'
                    dplg_b = f'{tplus_b} {a["pulang_b"]}'
                    
                    msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
                    plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
                    dselisih_b = plg_b - msk_b
                    # if dselisih_b.hour < 10
                    djam_selisih_b = f'{a["tgl_absen"]} {dselisih_b}'
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
            if a["istirahat"] is not None and a["kembali"] is not None:
                if a["kembali"] > a["istirahat"]:
                    
                    dist = f'{a["tgl_absen"]} {a["istirahat"]}'
                    dkmb = f'{a["tgl_absen"]} {a["kembali"]}'
                    
                    ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
                    kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_i = kmb - ist
                    djam_selisih_i = f'{a["tgl_absen"]} {dselisih_i}'
                    selisih_i = datetime.strptime(djam_selisih_i, '%Y-%m-%d %H:%M:%S')
                        
                    detik_i = selisih_i.second / 3600
                    menit_i = selisih_i.minute / 60
                    hour_i = selisih_i.hour
                    
                    jam_i = int(hour_i) + float(menit_i) + float(detik_i)
                    
                    tji = jam_i                   
                else:
                    
                    tplus = a["tgl_absen"] + timedelta(days=1)
                    
                    dist = f'{a["tgl_absen"]} {a["istirahat"]}'
                    dkmb = f'{tplus} {a["kembali"]}'
                    
                    ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
                    kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_i = kmb - ist
                    djam_selisih_i = f'{a["tgl_absen"]} {dselisih_i}'
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
            
            if a["istirahat_b"] is not None and a["kembali_b"] is not None:
                if a["kembali_b"] > a["istirahat_b"]:
                    
                    dist_b = f'{a["tgl_absen"]} {a["istirahat_b"]}'
                    dkmb_b = f'{a["tgl_absen"]} {a["kembali_b"]}'
                    
                    ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
                    kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_i_b = kmb_b - ist_b
                    djam_selisih_i_b = f'{a["tgl_absen"]} {dselisih_i_b}'
                    selisih_i_b = datetime.strptime(djam_selisih_i_b, '%Y-%m-%d %H:%M:%S')
                        
                    detik_i_b = selisih_i_b.second / 3600
                    menit_i_b = selisih_i_b.minute / 60
                    hour_i_b = selisih_i_b.hour
                    
                    jam_i_b = int(hour_i_b) + float(menit_i_b) + float(detik_i_b)
                    
                    tji_b = jam_i_b                   
                else:
                    if int(a["pegawai"].status.id) == 3:
                        tplus_b = a["tgl_absen"] + timedelta(days=1)
                    else:
                        tplus_b = a["tgl_absen"]
                    dist_b = f'{a["tgl_absen"]} {a["istirahat_b"]}'
                    dkmb_b = f'{tplus_b} {a["kembali_b"]}'
                    
                    ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
                    kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_i_b = kmb_b - ist_b
                    djam_selisih_i_b = f'{a["tgl_absen"]} {dselisih_i_b}'
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
            if a["istirahat2"] is not None and a["kembali2"] is not None:
                if a["kembali2"] > a["istirahat2"]:
                    
                    dist2 = f'{a["tgl_absen"]} {a["istirahat2"]}'
                    dkmb2 = f'{a["tgl_absen"]} {a["kembali2"]}'
                    
                    ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
                    kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_i2 = kmb2 - ist2
                    djam_selisih_i2 = f'{a["tgl_absen"]} {dselisih_i2}'
                    selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                        
                    detik_i2 = selisih_i2.second / 3600
                    menit_i2 = selisih_i2.minute / 60
                    hour_i2 = selisih_i2.hour
                    
                    jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
                    
                    tji2 = jam_i2                   
                else:
                    
                    tplus = a["tgl_absen"] + timedelta(days=1)
                    
                    dist2 = f'{a["tgl_absen"]} {a["istirahat2"]}'
                    dkmb2 = f'{tplus} {a["kembali2"]}'
                    
                    ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
                    kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_i2 = kmb2 - ist2
                    djam_selisih_i2 = f'{a["tgl_absen"]} {dselisih_i2}'
                    selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                        
                    detik_i2 = selisih_i2.second / 3600
                    menit_i2 = selisih_i2.minute / 60
                    hour_i2 = selisih_i2.hour
                    
                    jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
                    
                    tji2 = jam_i2
            else:
                tji2 = 0   
            if a["istirahat2_b"] is not None and a["kembali2_b"] is not None:
                if a["kembali2_b"] > a["istirahat2_b"]:
                    
                    dist2_b = f'{a["tgl_absen"]} {a["istirahat2_b"]}'
                    dkmb2_b = f'{a["tgl_absen"]} {a["kembali2_b"]}'
                    
                    ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
                    kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_i2_b = kmb2_b - ist2_b
                    djam_selisih_i2_b = f'{a["tgl_absen"]} {dselisih_i2_b}'
                    selisih_i2_b = datetime.strptime(djam_selisih_i2_b, '%Y-%m-%d %H:%M:%S')
                        
                    detik_i2_b = selisih_i2_b.second / 3600
                    menit_i2_b = selisih_i2_b.minute / 60
                    hour_i2_b = selisih_i2_b.hour
                    
                    jam_i2_b = int(hour_i2_b) + float(menit_i2_b) + float(detik_i2_b)
                    
                    tji2_b = jam_i2_b                   
                else:
                    
                    if int(a["pegawai__status_id"]) == 3:
                        tplus_b = a["tgl_absen"] + timedelta(days=1)
                    else:
                        tplus_b = a["tgl_absen"]
                    
                    dist2_b = f'{a["tgl_absen"]} {a["istirahat2_b"]}'
                    dkmb2_b = f'{tplus_b} {a["kembali2_b"]}'
                    
                    ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
                    kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih_i2_b = kmb2_b - ist2_b
                    djam_selisih_i2_b = f'{a["tgl_absen"]} {dselisih_i2_b}'
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
                        opgdr.append({
                            'id':0,
                            'idp':a["pegawai_id"],
                            'opg_tgl':a["tgl_absen"],
                            'diambil_tgl':"",
                            'keterangan':"OFF Pengganti Reguler"
                        })
                        insertopg.append(opg_db(pegawai_id=a["pegawai_id"],opg_tgl=a["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))

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
            a["total_jam_kerja"] = tjk + tjk_b
            a["total_jam_istirahat"] = tji + tji_b
            a["total_jam_istirahat2"] = tji2 + tji2_b
        
        end = time.perf_counter()
        print(f"PROSES ABSENSI LOOP OPG DLL {end-startsec} detik")

        start = time.perf_counter()
        absensi_db.objects.using(cabang).bulk_update([absensi_db(id=abs["id"],pegawai_id=abs["pegawai_id"],tgl_absen=abs["tgl_absen"],masuk=abs["masuk"],istirahat=abs['istirahat'],kembali=abs["kembali"],istirahat2=abs["istirahat2"],kembali2=abs["kembali2"],pulang=abs["pulang"],masuk_b=abs["masuk_b"],istirahat_b=abs["istirahat_b"],kembali_b=abs["kembali_b"],istirahat2_b=abs["istirahat2_b"],kembali2_b=abs["kembali2_b"],pulang_b=abs["pulang_b"],keterangan_absensi=abs["keterangan_absensi"],keterangan_ijin=abs["keterangan_ijin"],keterangan_lain=abs["keterangan_lain"],libur_nasional=abs["libur_nasional"],insentif=abs["insentif"],jam_masuk=abs["jam_masuk"],jam_pulang=abs["jam_pulang"],lama_istirahat=abs["lama_istirahat"],shift=abs["shift"],total_jam_kerja=abs["total_jam_kerja"],total_jam_istirahat=abs["total_jam_istirahat"],total_jam_istirahat2=abs["total_jam_istirahat2"],edit_by=abs["edit_by"]) for abs in data],["pegawai_id","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift"],batch_size=2300)  
        end = time.perf_counter()
        print(f"PROSES ABSENSI OPG DLL UPDATE {end-start} detik. {len(data)}")


        opg_db.objects.using(cabang).bulk_create(insertopg,batch_size=2300)

        print(datetime.now())
        endglobal = time.perf_counter()
        print(f"SEMUA DIPROSES DALAM WAKTU {endglobal - startglobal} detik")
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        return redirect("absensi",sid=int(sid))
    
    # return render("test"
    return redirect ('absensi_tgl',sid=int(sid),dr=dr,sp=sp)   

@authorization(["*"])
def detail_absensi(r,userid,tgl,sid,dr,sp):
    iduser = r.session['user']['id']
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses

        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)
        divisi = [div.divisi for div in aksesdivisi]

        dsid = dakses.sid_id  

        pgw = pegawai_db.objects.using(r.session["ccabang"]).filter(userid=userid,divisi__in=divisi)
        if not pgw.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pgw = pgw[0]
        # get absensi
        ab = absensi_db.objects.using(r.session["ccabang"]).get(pegawai__userid=userid,tgl_absen=tgl)

        # get all jam kerja 

        status = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).all().order_by('id')
        

        # get kk 
        if pgw.kelompok_kerja is not None:
            kk = jamkerja_db.objects.using(r.session["ccabang"]).filter(kk_id=pgw.kelompok_kerja.pk)
        else:
            kk = []
        dt_kk = []
        for k in kk:
            obj = {
                "kk":k.kk.kelompok,
                "jam_masuk":k.jam_masuk.strftime('%H:%M:%S'),
                "jam_pulang": k.jam_pulang.strftime('%H:%M:%S'),
                "lama_istirahat":k.lama_istirahat,
                # "lama_istirahat2":k.lama_istirahat
                "hari":k.hari
            }
            dt_kk.append(obj)

        ###
        sid_lembur = 0



        frmt = datetime.strptime(tgl, '%Y-%m-%d')
        nh = frmt.strftime('%A')
        nh = list(nama_hari(nh))
        nh = nh[0] + nh[1] + nh[2]
        nm = list(nama_bulan(frmt.month))
        nm = nm[0] + nm[1] + nm[2]


        data = {
                'akses' : akses,
                "cabang":r.session["cabang"],
                "ccabang":r.session["ccabang"],
                'status' : status,
                "nama":r.session["user"]["nama"],
                'dsid': dsid,
                'sid': sid,
                'sil': sid_lembur,
                "pegawai":pgw,
                'userid':pgw.userid,
                "dr":dr,
                "sp":sp,
                "nh":nh,
                "nm":nm,
                "day":frmt.day,
                'tgl':str(frmt.date()),
                "tahun":frmt.year,
                "ab":ab,
                "kk":dt_kk,
                'modul_aktif' : 'Absensi'
            }
            
        return render(r,'hrd_app/absensi/dabsen/[userid]/[tgl]/[sid]/dabsensi.html', data)
    
@authorization(["*"])
def get_trans_json(r):

        # get raw data absensi
    userid = r.GET.get('userid')
    tgl = datetime.strptime(r.GET.get('tgl'),"%Y-%m-%d")
    raw = data_trans_db.objects.using(r.session["ccabang"]).filter(userid=userid,jam_absen__date=tgl.date()).order_by("jam_absen")
    draw = []
    for i in raw:
        obj = {
            'id':i.pk,
            "userid":i.userid,
            "jam_absen":i.jam_absen.time().strftime('%H:%M:%S'),
            "punch":i.punch,
            "mesin":i.mesin,
            "ket":i.keterangan
        }
        draw.append(obj)
    
    return JsonResponse({"data":draw},safe=False)
    
@authorization(["*"])
def get_raw_json(r):

        # get raw data absensi
    userid = r.POST.get('userid')
    tgl = datetime.strptime(r.POST.get('tgl'),"%Y-%m-%d")
    tmin = tgl - timedelta(days=1)
    tplus = tgl + timedelta(days=2)
    raw = data_raw_db.objects.using(r.session["ccabang"]).filter(userid=userid,jam_absen__range=[tmin,tplus]).order_by("jam_absen")
    draw = []
    for i in raw:
        obj = {
            'id':i.pk,
            "userid":i.userid,
            "tgl":i.jam_absen.date(),
            "jam_absen":i.jam_absen.time().strftime('%H:%M:%S'),
            "punch":i.punch,
        }
        draw.append(obj)
    
    return JsonResponse({"data":draw},safe=False)
    

@authorization(["*"])
def hapus_jam(r):
    if r.headers['x-requested-with'] == 'XMLHttpRequest':
        id_user = r.session['user']['id']
        akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=int(id_user)).last()
        if akses is not None:
            id = r.POST.get('id')
            if id is not None:
                data_trans_db.objects.using(r.session["ccabang"]).get(pk=int(id)).delete()
            else:
                pass
        else:
            return JsonResponse({"status":"error","msg":"Akses anda belum ditentukan"},status=400)
    return JsonResponse({"ok":"ok"})

@authorization(["*"])
def tambah_jam(r):
    if r.headers['x-requested-with'] == 'XMLHttpRequest':
        tgl = datetime.strptime(r.POST.get("tgl"),"%Y-%m-%d")
        idp = r.POST.get("idp")
        jam_absen = datetime.combine(tgl,datetime.strptime(r.POST.get("jam_absen"),"%H:%M").time())
        absen = r.POST.get("absen")
        absen = absen.split("|")
        data_trans_db(
            userid = idp,
            jam_absen = jam_absen,
            punch = absen[0], 
            keterangan = absen[1],
            mesin = 'Manual'
        ).save(using=r.session["ccabang"])
        return JsonResponse({"status":"ok"})
    
@authorization(["*"])
def ubah_absen(r):
    id = r.POST.get('id')
    absen = r.POST.get('absen')
    absen = absen.split("|")

    if data_trans_db.objects.using(r.session["ccabang"]).filter(pk=int(id)).exists():
        ab = data_trans_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        ab.punch = absen[0]
        ab.keterangan = absen[1]
        ab.save(using=r.session["ccabang"])
    return JsonResponse({"ok":"ok"})

@authorization(["*"])
def pu(r,tgl,userid,sid,dr,sp):
    dt = data_trans_db.objects.using(r.session["ccabang"]).filter(jam_absen__date=tgl,userid=userid).order_by('jam_absen')
    id_user = r.session['user']['id']
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    abs = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").filter(tgl_absen=tgl,pegawai__userid=userid,pegawai__divisi__in=divisi).values("id","pegawai_id","pegawai__userid","pegawai__kelompok_kerja_id","pegawai__hari_off__hari","pegawai__hari_off2__hari","pegawai__status_id","pegawai__status__status","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift").last()
    if not abs:
        messages.error(r,"Anda tidak memiliki akses")
        return redirect("absensi",sid=sid)
    else:
        pass
    print(abs)
    abs["masuk"] = None
    abs["pulang"] = None
    abs["istirahat"] = None
    abs["kembali"] = None
    abs["pulang"] = None
    abs["masuk_b"] = None
    abs["istirahat_b"] = None
    abs["kembali_b"] = None
    abs["pulang_b"] = None
    abs["istirahat2"] = None
    abs["istirahat2_b"] = None
    abs["kembali2"] = None
    abs["kembali2_b"] = None
    for d in dt:
        if d.punch == 0:
            abs["masuk"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 1:
            abs["pulang"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 2:
            abs["istirahat"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 3:
            abs["kembali"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 4:
            abs["istirahat2"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 5:
            abs["kembali2"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 6:
            abs["masuk"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 7:
            abs["pulang"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 8:
            abs["istirahat"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 9:
            abs["kembali"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 10:
            abs["masuk_b"] = d.jam_absen.time().strftime('%H:%M:%S') 
        elif d.punch == 11:
            abs["pulang_b"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 12:
            abs["istirahat_b"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 13:
            abs["kembali_b"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 14:
            abs["istirahat2_b"] = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 15:
            abs["kembali2_b"] = d.jam_absen.time().strftime('%H:%M:%S')
    ijin = []  
    libur = []
    cuti = []
    geser = []
    geserdr = []
    kompen = []
    opg = []
    opgdr = []
    dl = []
    dl_idp = []
    ijindl = []
    lsopg = []
    
    # list status pegawai yang dapat opg
    for s in list_pegawai_opg_db.objects.using(r.session["ccabang"]).all():
        lsopg.append(s.pegawai_id)
    # data ijin
    for i in ijin_db.objects.using(r.session["ccabang"]).select_related('ijin','pegawai').filter(tgl_ijin=tgl).values("ijin__jenis_ijin","tgl_ijin","pegawai_id","keterangan"):
        data = {
            "ijin" : i["ijin__jenis_ijin"],
            "tgl_ijin" : i["tgl_ijin"],
            "idp" : i["pegawai_id"],
            "keterangan" : i["keterangan"]
        }
        ijin.append(data)
    
    # data libur nasional
    for l in libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur=tgl).values("libur","tgl_libur","insentif_karyawan","insentif_staff"):
        data = {
            'libur' : l["libur"],
            'tgl_libur' : l["tgl_libur"],
            'insentif_karyawan' : l["insentif_karyawan"],
            'insentif_staff' : l["insentif_staff"]
        }    
        libur.append(data)  
        
    # data cuti
    for c in cuti_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(tgl_cuti=tgl).values("id","pegawai_id","tgl_cuti","keterangan"):
        data = {
            'id': c["id"],
            'idp' : c["pegawai_id"],
            'tgl_cuti' : c["tgl_cuti"],
            'keterangan' : c["keterangan"]
        }                
        cuti.append(data)
        
    # data geser off
    for g in geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(ke_tgl=tgl).values("id","pegawai_id","dari_tgl","ke_tgl","keterangan"):
        data = {
            'id' : g["id"],
            'idp' : g["pegawai_id"], 
            'dari_tgl' : g["dari_tgl"],
            'ke_tgl' : g["ke_tgl"],
            'keterangan' : g["keterangan"]
        } 
        geser.append(data)
    for g in geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(dari_tgl=tgl).values("id","pegawai_id","dari_tgl","ke_tgl","keterangan"):
        data = {
            'id' : g["id"],
            'idp' : g["pegawai_id"], 
            'dari_tgl' : g["dari_tgl"],
            'ke_tgl' : g["ke_tgl"],
            'keterangan' : g["keterangan"]
        } 
        geserdr.append(data)
    status_ln = [st.pegawai_id for st in list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).all()]
    # data opg
    for o in opg_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(diambil_tgl=tgl).values("id","pegawai_id","opg_tgl","diambil_tgl","keterangan","status","edit_by"):
        data = {
            'id':o["id"],
            'idp': o["pegawai_id"],
            'opg_tgl':o["opg_tgl"],
            'diambil_tgl':o["diambil_tgl"],
            'keterangan':o["keterangan"],
            "status":o["status"],
            "edit_by":o["edit_by"]
        }
        opg.append(data)
    for odr in opg_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(opg_tgl=tgl).values("id","pegawai_id","opg_tgl","diambil_tgl","keterangan","status","edit_by"):
        data = {
            'id':odr["id"],
            'idp': odr["pegawai_id"],
            'opg_tgl':odr["opg_tgl"],
            'diambil_tgl':odr["diambil_tgl"],
            'keterangan':odr["keterangan"],
            "status":odr["status"],
            "edit_by":odr["edit_by"]
        }
        opgdr.append(data)
    
    # data dinas luar
    for n in dinas_luar_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(tgl_dinas=tgl).values("pegawai_id","tgl_dinas","keterangan"):
        data = {
            'idp': n["pegawai_id"],
            'tgl_dinas':n["tgl_dinas"],
            'keterangan':n["keterangan"]
        }
        dl.append(data)
        dl_idp.append(n.pegawai_id)
    for ij in ijin_db.objects.using(r.session["ccabang"]).filter(tgl_ijin=tgl).values("tgl_ijin","pegawai_id","ijin_id","ijin__jenis_ijin"):
        if re.search('(dinas luar|dl)',ij["ijin__jenis_ijin"],re.IGNORECASE) is not None:
            data = {
                "tgl":ij["tgl_ijin"],
                "idp":ij["pegawai_id"],
                "ijin":ij["ijin_id"]
            }
            ijindl.append(data)
    for k in kompen_db.objects.using(r.session["ccabang"]).all().values("id","pegawai_id","jenis_kompen","kompen","tgl_kompen"):
        data = {
            "idl":k["id"],
            "idp":k["pegawai_id"],
            "jenis_kompen":k["jenis_kompen"],
            "kompen":k["kompen"],
            "tgl_kompen":k["tgl_kompen"],
        }
        kompen.append(data)
        
    # data absensi
    if int(sid) == 0:
        data = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen=tgl).values("id","pegawai_id","pegawai__userid","pegawai__kelompok_kerja_id","pegawai__hari_off__hari","pegawai__hari_off2__hari","pegawai__status_id","pegawai__status__status","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift")
    elif int(sid) > 0:
        data = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen=tgl,pegawai__status_id=sid).values("id","pegawai_id","pegawai__userid","pegawai__kelompok_kerja_id","pegawai__hari_off__hari","pegawai__hari_off2__hari","pegawai__status_id","pegawai__status__status","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift")
    insertopg = []
    insertijin  = []
    username = r.session["user"]["nama"]
    cabang = r.session["ccabang"]
    day = abs["tgl_absen"].strftime("%A")
    nh = nama_hari(day)  
    """ Rules OPG (staff & karyawan) & Insentif (hanya untuk karyawan) :
    
    Staff :
    --> jika ada libur nasional dan jatuh di hari biasa (senin - sabtu), maka staff yang memiliki off reguler bertepatan
    dengan libur nasional tersebut akan mendapat opg = 2 jika masuk (off pengganti reguler dan off pengganti tgl merah), 
    jika tidak masuk mendapat opg = 1 (off pengganti reguler)
    
    --> jika ada libur nasional dan jatuh di hari minggu, maka staff yang memiliki off reguler bertepatan dengan libur
    nasional tersebut jika masuk mendapat opg = 1 (off pengganti reguler)
    
    --> jika tidak ada libur nasional, maka staff yang masuk di hari off regulernya maka mendapat opg = 1 (off pengganti 
    reguler)2
    
    Karyawan + SPG dibayar oleh Asia:
    --> jika ada libur nasional (senin - minggu), maka Karyawan yang memiliki off reguler bertepatan
    dengan libur nasional tersebut akan mendapat opg = 1 jika masuk (off pengganti reguler) dan insentif = 1
                    
    --> jika tidak ada libur nasional, maka Karyawan yang masuk di hari off regulernya maka mendapat opg = 1 (off pengganti 
    reguler)
    
    """  
    # OFF & OFF Pengganti Reguler
    # jika ada absen masuk dan pulang
    # rencana cronjob jalan
    if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
        if nh in [str(abs["pegawai__hari_off__hari"]),str(abs["pegawai__hari_off2__hari"])]:
            if abs["pegawai_id"] in lsopg and re.search("security",abs["pegawai__status__status"],re.IGNORECASE) is None and next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                opgdr.append({
                    'id':0,
                    'idp':abs["pegawai_id"],
                    'opg_tgl':abs["tgl_absen"],
                    'diambil_tgl':"",
                    'keterangan':"OFF Pengganti Reguler"
                })
                insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
            else:
                pass
        else: 
            if str(abs["pegawai__hari_off__hari"]) == "On Off":
                abs["keterangan_absensi"] = None
                    
    # jika tidak ada masuk dan pulang   
    else:
        # jika dinas luar
        if str(abs["pegawai__hari_off__hari"]) == 'On Off':
            abs["keterangan_absensi"] = 'OFF'
        for il in ijindl:
            if il["tgl"] == abs["tgl_absen"] and int(il["idp"]) == int(abs["pegawai_id"]) and nh in [str(abs["pegawai__hari_off__hari"]),str(abs["pegawai__hari_off2__hari"])] and  abs["pegawai_id"] in lsopg and next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                opgdr.append({
                    'id':0,
                    'idp':abs["pegawai_id"],
                    'opg_tgl':abs["tgl_absen"],
                    'diambil_tgl':"",
                    'keterangan':"OFF Pengganti Reguler"
                })
                insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
            else:
                pass
        # jika dia hari ini off
        if (abs["masuk"] is not None or abs["pulang"] is not None) or (abs["masuk_b"] is not None or abs["pulang_b"] is not None):
            if str(abs["pegawai__hari_off__hari"]) == "On Off":
                abs["keterangan_absensi"] = None
        else:
            if str(abs["pegawai__hari_off__hari"]) == str(nh):
                abs["keterangan_absensi"] = 'OFF'
            elif str(abs["pegawai__hari_off__hari"]) == 'On Off':
                abs["keterangan_absensi"] = 'OFF'
            if str(abs["pegawai__hari_off2__hari"]) == str(nh):
                abs["keterangan_absensi"] = 'OFF'
            else:
                pass   
        # jika hari ini dia adalah off nya
    
    # libur nasional
    for l in libur:
    # jika ada absen di hari libur nasional
        abs["libur_nasional"] = None
        if abs["pegawai_id"] in lsopg and l['tgl_libur'] == abs["tgl_absen"]:                            
            abs["libur_nasional"] = l['libur']
            
            # Hari Minggu
            if str(nh) == 'Minggu':                        
                    # Staff
                if abs["pegawai_id"] in status_ln: # regex
                    # jika hari off nya adalah hari minggu dan masuk maka hanya akan mendapatkan 1 opg
                    if str(nh) in [str(abs["pegawai__hari_off__hari"]), str(abs["pegawai__hari_off2__hari"])] and (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None) and next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                        opgdr.append({
                            'id':0,
                            'idp':abs["pegawai_id"],
                            'opg_tgl':abs["tgl_absen"],
                            'diambil_tgl':"",
                            'keterangan':"OFF Pengganti Reguler"
                        })
                        insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                    else:
                        pass                        
                # Karyawan
                else:
                    pass         
            
            # Bukan Hari Minggu
            else:                                                        
                # Staff
                if abs["pegawai_id"] in status_ln:
                    if str(nh) in [str(abs["pegawai__hari_off__hari"]), str(abs["pegawai__hari_off2__hari"])]:
                        # JIKA DIA MASUK DIHARI MERAH DILIBUR REGULERNYA MAKA AKAN DAPAT 2 OPG
                        if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                            if next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True):
                                if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):
                                    opgdr.append({
                                        'id':0,
                                        'idp':abs["pegawai_id"],
                                        'opg_tgl':abs["tgl_absen"],
                                        'diambil_tgl':"",
                                        'keterangan':"OFF Pengganti Reguler"
                                    })
                                    insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
                                    
                                if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                    opgdr.append({
                                        'id':0,
                                        'idp':abs["pegawai_id"],
                                        'opg_tgl':abs["tgl_absen"],
                                        'diambil_tgl':"",
                                        'keterangan':"OFF Pengganti Tgl Merah"
                                    })
                                    insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                        # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                        else:
                            if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                opgdr.append({
                                    'id':0,
                                    'idp':abs["pegawai_id"],
                                    'opg_tgl':abs["tgl_absen"],
                                    'diambil_tgl':"",
                                    'keterangan':"OFF Pengganti Tgl Merah"
                                })
                                insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                    # JIKA HARI OFF TIDAK BERTEPATAN HARI LIBUR NASIONAL
                    else:
                        if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                            if next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True):
                                if next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Tgl Merah"),True):
                                    opgdr.append({
                                        'id':0,
                                        'idp':abs["pegawai_id"],
                                        'opg_tgl':abs["tgl_absen"],
                                        'diambil_tgl':"",
                                        'keterangan':"OFF Pengganti Tgl Merah"
                                    })
                                    insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Tgl Merah",add_by="Program"))
                        # TAPI JIKA TIDAK MASUK HANYA MENDAPATKAN 1 OPG
                        else:
                            pass
                
                # Karyawan
                # JIKA MASUK HANYA MENDAPATKAN 1 OPG DAN INSENTIF
                else:
                    if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None) and next((False for gs in geserdr if gs["idp"] == abs["pegawai_id"] and gs["dari_tgl"] == abs["tgl_absen"]),True) and next((False for o in opgdr if o["idp"] == abs["pegawai_id"] and o["opg_tgl"] == abs["tgl_absen"] and o["keterangan"] == "OFF Pengganti Reguler"),True):                                        
                            abs["insentif"] = l['insentif_karyawan']
                    else:
                        pass    
                
    # ijin
    for i in ijin:
        if abs["pegawai_id"] == i['idp'] and i['tgl_ijin'] == abs["tgl_absen"]:
            ij = i['ijin']
            ket = i['keterangan']
            abs["keterangan_ijin"] = f'{ij}-({ket})'
        else:
            pass                                 
    
    for kmpn in kompen:
        if abs["pegawai_id"] == kmpn["idp"] and kmpn["tgl_kompen"] == abs["tgl_absen"]:
            if abs["jam_masuk"] is not None and abs["jam_pulang"] is None and abs["masuk"] is not None and abs["pulang"] is not None:
                if abs["pulang"] > abs["masuk"]:
                    jm = datetime.combine(abs["tgl_absen"],abs["jam_masuk"])
                    jp = datetime.combine(abs["tgl_absen"],abs["jam_pulang"])
                    
                    jkompen = float(kmpn["kompen"])
                    
                    if kmpn["jenis_kompen"] == 'awal':
                        njm = jm - timedelta(hours=jkompen)
                        njp = abs["jam_pulang"]
                    elif kmpn["jenis_kompen"] == 'akhir':    
                        njm = abs["jam_masuk"]
                        njp = jp + timedelta(hours=jkompen)
                    else:    
                        njm = jm - timedelta(hours=jkompen)
                        njp = jp + timedelta(hours=jkompen)
                    
                    dmsk = f'{abs["tgl_absen"]} {abs["masuk"]}'
                    dplg = f'{abs["tgl_absen"]} {abs["pulang"]}'
                    
                    msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                    plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                    
                    dselisih = plg - msk
                    djam_selisih = f'{abs["tgl_absen"]} {dselisih}'
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
                    abs["jam_masuk"] = njm
                    abs["jam_pulang"] = njp
                else: 
                    tjk = 0   
            else:
                tjk = 0
            if kmpn["jenis_kompen"] == 'awal':
                abs["keterangan_lain"] = f"Kompen/PJK-Awal {kmpn['kompen']} Jam"
            elif kmpn["jenis_kompen"] == "akhir":
                abs["keterangan_lain"] = f"Kompen/PJK-Akhir {kmpn['kompen']} Jam"
            else:
                abs["keterangan_lain"] = f"Kompen/PJK 1 hari"
            nama_user = username
            abs["total_jam_kerja"] = round(tjk,1)
            abs["edit_by"] = nama_user
        else:
            pass
    
    # cuti
    for c in cuti:
        # jika didalam data cuti ada pegawai id
        if abs["pegawai_id"] == c['idp'] and c['tgl_cuti'] == abs["tgl_absen"]:
            # jika tidak masuk dan pulang
            if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                dmsk = f'{abs["tgl_absen"]} {abs["masuk"]}'
                dplg = f'{abs["tgl_absen"]} {abs["pulang"]}'
                
                msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                
                dselisih = plg - msk
                djam_selisih = f'{abs["tgl_absen"]} {dselisih}'
                selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S') 
                # jika jam kerja kurang dari 4 jam
                if int(selisih.hour) <= 4:
                    abs["keterangan_absensi"] = c['keterangan']
                # jika jam kerja lebih dari 4 jam
                else:
                    cuti_db.objects.using(cabang).get(id=int(c['id'])).delete()
                    pg = pegawai_db.objects.using(cabang).get(pk=abs["pegawai_id"])
                    sc = pg.sisa_cuti
                    abs["keterangan_absensi"] = ""
                    pg.sisa_cuti = sc + 1
                    pg.save(using=cabang)          
            else:
                abs["keterangan_absensi"] = c['keterangan']
        else:
            pass        
        
    # geser off
    for g in geser:
        if abs["pegawai_id"] == g['idp']:
            if g['ke_tgl'] == abs["tgl_absen"]:
                # jika ada geser off dan dia tidak masuk
                if (abs["masuk"] is None and abs["pulang"] is None) or (abs["masuk_b"] is None and abs["pulang_b"] is None):
                    drt = datetime.strftime(g['dari_tgl'], '%d-%m-%Y')
                    abs["keterangan_absensi"] = f'Geser OFF-({drt})' 
                # jika ada geser off dan dia masuk
                else:
                    geseroff_db.objects.using(cabang).get(id=int(g['id'])).delete()    
            elif g["dari_tgl"] == abs["tgl_absen"]:
                if (abs["masuk"] is not None and abs["pulang"] is not None) or (abs["masuk_b"] is not None and abs["pulang_b"] is not None):
                    abs["keterangan_absensi"] = None
                else:
                    pass
            else:
                pass
        else:
            pass
    # opg
    for o in opg:
        if abs["pegawai_id"] == o['idp'] and o['diambil_tgl'] == abs["tgl_absen"]:
            opg_detail = opg_db.objects.using(cabang).get(pk=int(o["id"]))
            # jika tidak masuk dan tidak ada pulang
            if abs["masuk"] is None and abs["pulang"] is None and abs["masuk_b"] is None and abs["pulang_b"] is None:
                topg = datetime.strftime(o['opg_tgl'], '%d-%m-%Y')
                abs["keterangan_absensi"] = f'OPG-({topg})'
                
                opg_detail.status = 1
                opg_detail.edit_by ='Program'
                opg_detail.save(using=cabang)
            # jika masuk dan pulang
            else:
                opg_detail["diambil_tgl"] = None
                opg_detail.edit_by = 'Program'
                opg_detail.save(using=cabang)
                    
        else:
            pass        
    
    # dinas luar   
    for n in dl:
        if abs["pegawai_id"] == n['idp'] and n['tgl_dinas'] == abs["tgl_absen"]:
            ket = n['keterangan']
            abs["keterangan_absensi"] = f'Dinas Luar-({ket})'
        else:
            pass    
                            
    # total jam kerja         
    if abs["masuk"] is not None and abs["pulang"] is not None:
        if abs["pulang"] > abs["masuk"]:
            
            dmsk = f'{abs["tgl_absen"]} {abs["masuk"]}'
            dplg = f'{abs["tgl_absen"]} {abs["pulang"]}'
            
            msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
            plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
            
            dselisih = plg - msk
            djam_selisih = f'{abs["tgl_absen"]} {dselisih}'
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
            
            tplus = abs["tgl_absen"]        
            
            dmsk = f'{abs["tgl_absen"]} {abs["masuk"]}'
            dplg = f'{tplus} {abs["pulang"]}'
            
            msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
            plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
            
            dselisih = plg - msk
            djam_selisih = f'{abs["tgl_absen"]} {dselisih}'
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
    if abs["masuk_b"] is not None and abs["pulang_b"] is not None:
        if abs["pulang_b"] > abs["masuk_b"]:
            
            dmsk_b = f'{abs["tgl_absen"]} {abs["masuk_b"]}'
            dplg_b = f'{abs["tgl_absen"]} {abs["pulang_b"]}'
            
            msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
            plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
            
            dselisih_b = plg_b - msk_b
            djam_selisih_b = f'{abs["tgl_absen"]} {dselisih_b}'
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
            
            tplus_b = abs["tgl_absen"]
            dmsk_b = f'{abs["tgl_absen"]} {abs["masuk_b"]}'
            dplg_b = f'{tplus_b} {abs["pulang_b"]}'
            
            msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
            plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
            dselisih_b = plg_b - msk_b
            # if dselisih_b.hour < 10
            djam_selisih_b = f'{abs["tgl_absen"]} {dselisih_b}'
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
    if abs["istirahat"] is not None and abs["kembali"] is not None:
        if abs["kembali"] > abs["istirahat"]:
            
            dist = f'{abs["tgl_absen"]} {abs["istirahat"]}'
            dkmb = f'{abs["tgl_absen"]} {abs["kembali"]}'
            
            ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
            kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
            
            dselisih_i = kmb - ist
            djam_selisih_i = f'{abs["tgl_absen"]} {dselisih_i}'
            selisih_i = datetime.strptime(djam_selisih_i, '%Y-%m-%d %H:%M:%S')
                
            detik_i = selisih_i.second / 3600
            menit_i = selisih_i.minute / 60
            hour_i = selisih_i.hour
            
            jam_i = int(hour_i) + float(menit_i) + float(detik_i)
            
            tji = jam_i                   
        else:
            
            tplus = abs["tgl_absen"] + timedelta(days=1)
            
            dist = f'{abs["tgl_absen"]} {abs["istirahat"]}'
            dkmb = f'{tplus} {abs["kembali"]}'
            
            ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
            kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
            
            dselisih_i = kmb - ist
            djam_selisih_i = f'{abs["tgl_absen"]} {dselisih_i}'
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
    
    if abs["istirahat_b"] is not None and abs["kembali_b"] is not None:
        if abs["kembali_b"] > abs["istirahat_b"]:
            
            dist_b = f'{abs["tgl_absen"]} {abs["istirahat_b"]}'
            dkmb_b = f'{abs["tgl_absen"]} {abs["kembali_b"]}'
            
            ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
            kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
            
            dselisih_i_b = kmb_b - ist_b
            djam_selisih_i_b = f'{abs["tgl_absen"]} {dselisih_i_b}'
            selisih_i_b = datetime.strptime(djam_selisih_i_b, '%Y-%m-%d %H:%M:%S')
                
            detik_i_b = selisih_i_b.second / 3600
            menit_i_b = selisih_i_b.minute / 60
            hour_i_b = selisih_i_b.hour
            
            jam_i_b = int(hour_i_b) + float(menit_i_b) + float(detik_i_b)
            
            tji_b = jam_i_b                   
        else:
            if int(abs["pegawai"].status.id) == 3:
                tplus_b = abs["tgl_absen"] + timedelta(days=1)
            else:
                tplus_b = abs["tgl_absen"]
            dist_b = f'{abs["tgl_absen"]} {abs["istirahat_b"]}'
            dkmb_b = f'{tplus_b} {abs["kembali_b"]}'
            
            ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
            kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
            
            dselisih_i_b = kmb_b - ist_b
            djam_selisih_i_b = f'{abs["tgl_absen"]} {dselisih_i_b}'
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
    if abs["istirahat2"] is not None and abs["kembali2"] is not None:
        if abs["kembali2"] > abs["istirahat2"]:
            
            dist2 = f'{abs["tgl_absen"]} {abs["istirahat2"]}'
            dkmb2 = f'{abs["tgl_absen"]} {abs["kembali2"]}'
            
            ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
            kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
            
            dselisih_i2 = kmb2 - ist2
            djam_selisih_i2 = f'{abs["tgl_absen"]} {dselisih_i2}'
            selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                
            detik_i2 = selisih_i2.second / 3600
            menit_i2 = selisih_i2.minute / 60
            hour_i2 = selisih_i2.hour
            
            jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
            
            tji2 = jam_i2                   
        else:
            
            tplus = abs["tgl_absen"] + timedelta(days=1)
            
            dist2 = f'{abs["tgl_absen"]} {abs["istirahat2"]}'
            dkmb2 = f'{tplus} {abs["kembali2"]}'
            
            ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
            kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
            
            dselisih_i2 = kmb2 - ist2
            djam_selisih_i2 = f'{abs["tgl_absen"]} {dselisih_i2}'
            selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                
            detik_i2 = selisih_i2.second / 3600
            menit_i2 = selisih_i2.minute / 60
            hour_i2 = selisih_i2.hour
            
            jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
            
            tji2 = jam_i2
    else:
        tji2 = 0   
    if abs["istirahat2_b"] is not None and abs["kembali2_b"] is not None:
        if abs["kembali2_b"] > abs["istirahat2_b"]:
            
            dist2_b = f'{abs["tgl_absen"]} {abs["istirahat2_b"]}'
            dkmb2_b = f'{abs["tgl_absen"]} {abs["kembali2_b"]}'
            
            ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
            kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
            
            dselisih_i2_b = kmb2_b - ist2_b
            djam_selisih_i2_b = f'{abs["tgl_absen"]} {dselisih_i2_b}'
            selisih_i2_b = datetime.strptime(djam_selisih_i2_b, '%Y-%m-%d %H:%M:%S')
                
            detik_i2_b = selisih_i2_b.second / 3600
            menit_i2_b = selisih_i2_b.minute / 60
            hour_i2_b = selisih_i2_b.hour
            
            jam_i2_b = int(hour_i2_b) + float(menit_i2_b) + float(detik_i2_b)
            
            tji2_b = jam_i2_b                   
        else:
            
            if int(abs["pegawai__status_id"]) == 3:
                tplus_b = abs["tgl_absen"] + timedelta(days=1)
            else:
                tplus_b = abs["tgl_absen"]
            
            dist2_b = f'{abs["tgl_absen"]} {abs["istirahat2_b"]}'
            dkmb2_b = f'{tplus_b} {abs["kembali2_b"]}'
            
            ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
            kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
            
            dselisih_i2_b = kmb2_b - ist2_b
            djam_selisih_i2_b = f'{abs["tgl_absen"]} {dselisih_i2_b}'
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
                opgdr.append({
                    'id':0,
                    'idp':abs["pegawai_id"],
                    'opg_tgl':abs["tgl_absen"],
                    'diambil_tgl':"",
                    'keterangan':"OFF Pengganti Reguler"
                })
                insertopg.append(opg_db(pegawai_id=abs["pegawai_id"],opg_tgl=abs["tgl_absen"],keterangan="OFF Pengganti Reguler",add_by="Program"))
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
    abs["total_jam_kerja"] = tjk + tjk_b
    abs["total_jam_istirahat"] = tji + tji_b
    abs["total_jam_istirahat2"] = tji2 + tji2_b
    absensi_db.objects.using(cabang).bulk_update([absensi_db(id=abs["id"],pegawai_id=abs["pegawai_id"],tgl_absen=abs["tgl_absen"],masuk=abs["masuk"],istirahat=abs['istirahat'],kembali=abs["kembali"],istirahat2=abs["istirahat2"],kembali2=abs["kembali2"],pulang=abs["pulang"],masuk_b=abs["masuk_b"],istirahat_b=abs["istirahat_b"],kembali_b=abs["kembali_b"],istirahat2_b=abs["istirahat2_b"],kembali2_b=abs["kembali2_b"],pulang_b=abs["pulang_b"],keterangan_absensi=abs["keterangan_absensi"],keterangan_ijin=abs["keterangan_ijin"],keterangan_lain=abs["keterangan_lain"],libur_nasional=abs["libur_nasional"],insentif=abs["insentif"],jam_masuk=abs["jam_masuk"],jam_pulang=abs["jam_pulang"],lama_istirahat=abs["lama_istirahat"],shift=abs["shift"],total_jam_kerja=abs["total_jam_kerja"],total_jam_istirahat=abs["total_jam_istirahat"],total_jam_istirahat2=abs["total_jam_istirahat2"],edit_by=abs["edit_by"])],["pegawai_id","tgl_absen","masuk","istirahat","kembali","istirahat2","kembali2","pulang","masuk_b","istirahat_b","kembali_b","istirahat2_b","kembali2_b","pulang_b","keterangan_absensi","keterangan_ijin","keterangan_lain","libur_nasional","insentif","jam_masuk","jam_pulang","lama_istirahat","total_jam_kerja","total_jam_istirahat","total_jam_istirahat2","edit_by","shift"]) 
    opg_db.objects.using(cabang).bulk_create(insertopg)
    # red = redis.Redis(host="15.63.254.114", port="6370", decode_responses=True, username="azril", password=132)
    # for s in red.scan_iter(f"absensi-*{abs.tgl_absen.strftime('%Y-%m-%d')}*-{sid}"):
    #     
    #     red.delete(s)
    return redirect("dabsen",userid=userid,tgl=tgl,sid=sid,dr=dr,sp=sp)

@authorization(["*"])
def edit_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")
    ket = r.POST.get("ket")
    id = r.POST.get("id")
    sid = r.POST.get("sid")
    id_user = r.session['user']['id']
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    if jenis_ijin_db.objects.using(r.session["ccabang"]).filter(pk=int(jenis_ijin)).exists():
        if absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").filter(pk=int(id),pegawai__divisi__in=divisi).exists():
            ji = jenis_ijin_db.objects.using(r.session["ccabang"]).get(pk=int(jenis_ijin))
            ab = absensi_db.objects.using(r.session["ccabang"]).get(pk=int(id))
            ab.keterangan_ijin = f'{ji.jenis_ijin}-({ket})'
            ab.save(using=r.session["ccabang"])
            ijin_db(
                pegawai_id = ab.pegawai_id,
                tgl_ijin = ab.tgl_absen,
                ijin_id = ji.pk,
                keterangan = ket,
                add_by = 'Program'
            ).save(using=r.session["ccabang"])
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("absensi",sid=sid)
    return JsonResponse({"ok":"ok"})

@authorization(["*"])
def edit_jamkerja(r,userid,tgl,sid,dr,sp):
    masuk = r.POST.get("jam_masuk")
    keluar = r.POST.get("jam_keluar")
    lama_ist = r.POST.get("lama_istirahat")
    id = r.POST.get("id")
    if masuk == '' or keluar == "" or lama_ist == "":
        messages.add_message(r,messages.ERROR,"Form harus lengkap")
        return redirect("dabsen",userid=userid,tgl=tgl,sid=sid)
    id_user = r.session['user']['id']
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    if absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").filter(pk=int(id),pegawai__divisi__in=divisi).exists():
        ab = absensi_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        ab.jam_masuk = masuk
        ab.jam_pulang = keluar
        ab.lama_istirahat = lama_ist
        ab.save(using=r.session["ccabang"])
    else:
        messages.error(r,"Anda tidak memiliki akses")
        return redirect("absensi",sid=sid)
    return redirect("dabsen",userid=userid,tgl=tgl,sid=sid,dr=dr,sp=sp)

@authorization(["*"])
def absensi_id(r):
    idp = r.POST.get('id')
    tgl = r.POST.get('tgl')
    tgl = datetime.strptime(tgl,"%d-%m-%Y")
    tgl = tgl.strftime("%Y-%m-%d")
    if absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=idp,tgl_absen=tgl).exists():
        ab = absensi_db.objects.using(r.session["ccabang"]).get(pegawai_id=idp,tgl_absen=tgl)
        data = {
            "lama_istirahat":ab.lama_istirahat,
            "lama_istirahat2":ab.lama_istirahat2,
        }
        return JsonResponse({"status":"ok","data":data})
    else:
        return JsonResponse({"status":"null","data":{}})
