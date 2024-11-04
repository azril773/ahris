from hrd_app.controllers.lib import *
import pika
import threading
from concurrent.futures import ThreadPoolExecutor
from django.db import connection
from multiprocessing import Pool
from hrd_app.function import prosesabsensi
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Absensi
@login_required
def absensi(r,sid):
    iduser = r.user.id
        
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
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        jenis_ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).all()   
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur,
            'dari': dari,
            'sampai': sampai,
            'dr' : dr,
            'sp' : sp,
            'jenis_ijin' : jenis_ijin,
            'modul_aktif' : 'Absensi'
        }

        if r.session["ccabang"] != "tasik":
            return render(r,'hrd_app/absensi/absensi_non.html', data)
        else:
            return render(r,'hrd_app/absensi/absensi.html', data)
        
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_absensi(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        sid = r.POST.get('sid')
        dari = datetime.strptime(r.POST.get('ctgl1'),'%d-%m-%Y').date()
        sampai = datetime.strptime(r.POST.get('ctgl2'),'%d-%m-%Y').date()
        id_user = r.user.id
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
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
                    msk = '-'

                if a.pulang is not None:
                    plg = f"{a.pulang}"
                else:
                    plg = "-"
                    plg = '-'

                if a.masuk_b is not None:
                    msk_b = f"{a.masuk_b}"
                else:
                    msk_b = "-"
                    msk_b = '-'

                if a.pulang_b is not None:
                    plg_b = f"{a.pulang_b}"
                else:
                    plg_b = "-"
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


@login_required
def cari_absensi_sid(r,dr, sp, sid):
    iduser = r.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
                
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
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


@login_required
def absensi_json(r, dr, sp, sid):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.user.id
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        
        if int(sid) == 0:
            for a in absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__counter','pegawai__divisi').filter(pegawai__divisi__in=divisi,tgl_absen__range=(dari,sampai)).order_by('tgl_absen','pegawai__divisi__divisi'):
                sket = " "
                
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


def prosesMesin(m):
    ip = m[0].ipaddress
    # print(ip)
    # conn = None
    zk = ZK(str(ip), port=4370, timeout=65)
    dt = []
    try:
        conn = zk.connect()
        conn.disable_device()
        # Data absensi
        absensi = conn.get_attendance()
        for a in absensi:
            if m[2] <= a.timestamp <= m[3]:   
                # print(a.user_id) 
                # users = conn.get_users()
                # print([user for user in absensi if user.user_id == "226002"])
                if str(a.user_id) in m[1]:     
                    data = {
                        "userid": a.user_id, 
                        "jam_absen": datetime.strftime(a.timestamp,"%Y-%m-%d %H:%M:%S"),
                        "punch": a.punch,
                        "mesin": m[0].nama 
                    }
                    # print(data)
                    dt.append(data)
                else:
                    pass                
        conn.enable_device()
    except Exception as e:
        print(e)
        messages.error(m[4], "Process terminate : {}".format(e))
        # return redirect("absensi",sid=)
        return e
    finally:
        if conn:
            conn.disconnect()
        return dt

@login_required
def pabsen(req):    
    
    t1 = req.POST.get('tgl1')
    t2 = req.POST.get('tgl2')
    sid = req.POST.get('sid')
    
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
    id_user = req.user.id
    aksesdivisi = akses_divisi_db.objects.using(req.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    if int(sid) == 0:
        for p in pegawai_db.objects.using(req.session["ccabang"]).select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(divisi__in=divisi):
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
            pegawai.append(data)        
            luserid.append(p.userid)
            for tgl in rangetgl:
                if absensi_db.objects.using(req.session["ccabang"]).filter(tgl_absen=tgl, pegawai_id=p.id).exists():
                    pass
                else:
                    tabsen = absensi_db(
                        tgl_absen = tgl,
                        pegawai_id = p.id
                    )
                    tabsen.save(using=req.session["ccabang"])
    else:
        for p in pegawai_db.objects.using(req.session["ccabang"]).select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(divisi__in=divisi,status__id=sid):
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
                "status":p.status.status,
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
            pegawai.append(data)        
            luserid.append(p.userid)
            for tgl in rangetgl:
                if absensi_db.objects.using(req.session["ccabang"]).filter(tgl_absen=tgl, pegawai_id=p.id).exists():
                    pass
                else:
                    tabsen = absensi_db(
                        tgl_absen = tgl,
                        pegawai_id = p.id
                    )
                    tabsen.save(using=req.session['ccabang'])
    
    dmesin = []
    # ambil data mesin simpan di att dan dmesin array
    try:
        pools = Pool(processes=2
                     )
        for m in mesin_db.objects.using(req.session["ccabang"]).filter(status='Active'):
            ress = pools.apply_async(prosesMesin,[(m,luserid,dari,sampai)])
            # print(ress,"SDS")
            # time.sleep(1)
            dmesin.append(ress)
        msn = [mesin.wait() for mesin in dmesin]
        # print(dmesin)
        datas = [dt for dt in [dataMesin.get() for dataMesin in dmesin] if len(dt) > 0] 
        dmesin = []
        for dm in datas:
            for d in dm:    
                dmesin.append(d)
    except Exception as err:
        print(err)
        messages.error(req,"Terjadi kesalahan pada mesin finger. Silahkan coba lagi")
        return redirect("absensi",sid=sid)

    # return render(req,'hrd_app/example/ex.html')
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
    att = sorted(dmesin, key=lambda i: i['jam_absen'])

    # att = sorted(att, key=lambda i: i['jam_absen'])
    ddr = []
    # jika istirahat sama maka jan masukin ke b INGETTTT
    
        
    # ambil data raw simpan di ddr
    for d in data_raw_db.objects.using(req.session["ccabang"]).filter(jam_absen__range=(dari.date(),sampai.date()), userid__in=luserid):
        data = {
            "userid": d.userid,
            "jam_absen": d.jam_absen,
            "punch": d.punch,
            "mesin": d.mesin
        }

        ddr.append(data)              
    
    ddt = []
    
    # ambil data trans simpan di ddt
    for d2 in data_trans_db.objects.using(req.session["ccabang"]).filter(jam_absen__range=(dari.date(),sampai.date()), userid__in=luserid):
        data = {
            "userid": d2.userid,
            "jam_absen": d2.jam_absen,
            "punch": d2.punch,
            "mesin": d2.mesin,
            "ket": d2.keterangan
        }

        ddt.append(data)
        
    status_lh = [st.pk for st in status_pegawai_lintas_hari_db.objects.using(req.session["ccabang"]).all()]
    dt = []    
    # proses data simpan di dt array
    # obj 
    jamkerja = jamkerja_db.objects.using(req.session["ccabang"]).select_related('kk').all()
    now = datetime.now()
    hari = now.strftime("%A")
    hari = nama_hari(hari)


    if req.session["ccabang"] != "tasik":
        prosesabsensi.lh(att,luserid,ddr,rangetgl,pegawai,jamkerja,dt,status_lh,hari,req.session["ccabang"],ddt)
    else:
        prosesabsensi.nlh(att,luserid,ddr,rangetgl,pegawai,jamkerja,dt,status_lh,hari,req.session["ccabang"],ddt)

    # simpan data trans
    
    
    
    ijin = []  
    libur = []
    cuti = []
    geser = []
    geser_all = []
    opg = []
    opg_all = []
    dl = []
    dl_idp = []
    
    lsopg = []
    
    # list status pegawai yang dapat opg
    for s in list_status_opg_db.objects.using(req.session["ccabang"]).all():
        lsopg.append(s.status_id)
    
    # geser off all 
    for ga in geseroff_db.objects.using(req.session["ccabang"]).using(req.session["ccabang"]).all():
        data = {
            'id' : ga.id,
            'idp' : ga.pegawai_id, 
            'dari_tgl' : ga.dari_tgl,
            'ke_tgl' : ga.ke_tgl,
            'keterangan' : ga.keterangan
        } 
        geser_all.append(data)

    # opg all
    for oa in opg_db.objects.using(req.session["ccabang"]).all():
        data = {
            'id':oa.id,
            'idp': oa.pegawai_id,
            'opg_tgl':oa.opg_tgl,
            'diambil_tgl':oa.diambil_tgl,
            'keterangan':oa.keterangan
        }
        opg_all.append(data)


    # data ijin
    for i in ijin_db.objects.using(req.session["ccabang"]).select_related('ijin','pegawai').filter(tgl_ijin__range=(dari.date(),sampai.date())):
        data = {
            "ijin" : i.ijin.jenis_ijin,
            "tgl_ijin" : i.tgl_ijin,
            "idp" : i.pegawai_id,
            "keterangan" : i.keterangan
        }
        ijin.append(data)
    
    # data libur nasional
    for l in libur_nasional_db.objects.using(req.session["ccabang"]).filter(tgl_libur__range=(dari.date(),sampai.date())):
        data = {
            'libur' : l.libur,
            'tgl_libur' : l.tgl_libur,
            'insentif_karyawan' : l.insentif_karyawan,
            'insentif_staff' : l.insentif_staff
        }    
        libur.append(data)  
        
    # data cuti
    for c in cuti_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(tgl_cuti__range=(dari.date(),sampai.date())):
        data = {
            'id': c.id,
            'idp' : c.pegawai_id,
            'tgl_cuti' : c.tgl_cuti,
            'keterangan' : c.keterangan
        }                
        cuti.append(data)
        
    # data geser off
    for g in geseroff_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(ke_tgl__range=(dari.date(),sampai.date())):
        data = {
            'id' : g.id,
            'idp' : g.pegawai_id, 
            'dari_tgl' : g.dari_tgl,
            'ke_tgl' : g.ke_tgl,
            'keterangan' : g.keterangan
        } 
        geser.append(data)
    status_ln = [st.pk for st in list_status_opg_libur_nasional_db.objects.using(req.session["ccabang"]).all()]
    # data opg
    for o in opg_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(diambil_tgl__range=(dari.date(),sampai.date()), status=0):
        data = {
            'id':o.id,
            'idp': o.pegawai_id,
            'opg_tgl':o.opg_tgl,
            'diambil_tgl':o.diambil_tgl,
            'keterangan':o.keterangan
        }
        opg.append(data)
    
    # data dinas luar
    for n in dinas_luar_db.objects.using(req.session["ccabang"]).select_related('pegawai').filter(tgl_dinas__range=(dari.date(),sampai.date())):
        data = {
            'idp': n.pegawai_id,
            'tgl_dinas':n.tgl_dinas,
            'keterangan':n.keterangan
        }
        dl.append(data)
        dl_idp.append(n.pegawai_id)
        
    # data absensi
    if int(sid) == 0:
        data = absensi_db.objects.using(req.session["ccabang"]).select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen__range=(dari.date(),sampai.date()))
    elif int(sid) > 0:
        data = absensi_db.objects.using(req.session["ccabang"]).select_related('pegawai','pegawai__status',"pegawai__hari_off","pegawai__hari_off2").filter(tgl_absen__range=(dari.date(),sampai.date()),pegawai__status_id=sid)
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
                if a.pegawai.status_id in lsopg:
                    # jika ada geder off dari hari ini ke hari lain
                    if next((True for gs in geser_all if gs["idp"] == ab.pegawai_id and gs["dari_tgl"] == ab.tgl_absen),False):
                        pass
                    # jika tidak ada
                    else:
                        
                        if next((True for o in opg if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Reguler"),False):
                            pass
                        # jika tidak
                        else:
                            opg_db(
                                pegawai_id = ab.pegawai_id,
                                opg_tgl = ab.tgl_absen,   
                                keterangan = 'OFF Pengganti Reguler',                         
                                add_by = 'Program',
                            ).save(using=req.session["ccabang"])
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
                            ).save(using=req.session['ccabang'])
                else:
                    pass
            else:
                pass
                    
        # jika tidak ada masuk dan pulang   
        else:
            # jika dinas luar
            if ab.pegawai_id in dl_idp:
                
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
                                ).save(using=req.session['ccabang'])
                    else:
                        pass
                else:
                    # jika on off
                    if str(a.pegawai.hari_off) == 'On Off':
                        ab.keterangan_absensi = 'OFF'
                        ab.save(using=req.session["ccabang"])
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
                                ).save(using=req.session['ccabang'])
                    else:
                        pass
                else:
                    pass    
            else:
                # jika dia hari ini off
                if str(a.pegawai.hari_off) == str(nh):
                    ab.keterangan_absensi = 'OFF'
                    ab.save(using=req.session['ccabang'])
                elif str(a.pegawai.hari_off) == 'On Off':
                    ab.keterangan_absensi = 'OFF'
                    ab.save(using=req.session['ccabang'])    
                            
                if str(a.pegawai.hari_off2) == str(nh):
                    ab.keterangan_absensi = 'OFF'
                    ab.save(using=req.session['ccabang']) 
                else:
                    pass   
            # jika hari ini dia adalah off nya
        
        # libur nasional
        for l in libur:
        # jika ada absen di hari libur nasional
            ab.libur_nasional = None
            if l['tgl_libur'] == ab.tgl_absen:                            
                ab.libur_nasional = l['libur']
                ab.save(using=req.session["ccabang"])
                
                # Hari Minggu
                if str(nh) == 'Minggu':
                    if a.pegawai.status_id in lsopg:
                        
                        # Staff
                        if p['status'] == 'Staff': # regex
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
                                            ).save(using=req.session['ccabang'])
                                else:
                                    pass    
                            else:
                                pass
                        
                        # Karyawan
                        else:
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
                                            ).save(using=req.session["ccabang"])
                                            
                                            # ditasik tidak ada insentif dihari minggu jika masuk
                                            # ab.insentif = l['insentif_karyawan']
                                            # ab.save(using=req.session["ccabang"])
                                else:
                                    pass    
                            else:
                                pass                                
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
                                            ).save(using=req.session["ccabang"])
                                            
                                        if next((True for o in opg_all if o["idp"] == ab.pegawai_id and o["opg_tgl"] == ab.tgl_absen and o["keterangan"] == "OFF Pengganti Tgl Merah"),False):
                                            pass
                                        else:    
                                            opg_db(
                                                pegawai_id = ab.pegawai_id,
                                                opg_tgl = ab.tgl_absen,   
                                                keterangan = 'OFF Pengganti Tgl Merah',                         
                                                add_by = 'Program',
                                            ).save(using=req.session["ccabang"])
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
                                        ).save(using=req.session["ccabang"])    
                            else:
                                pass
                        
                        # Karyawan
                        # JIKA MASUK HANYA MENDAPATKAN 1 OPG DAN INSENTIF
                        else:
                            if str(a.pegawai.hari_off) == str(nh):
                                if (ab.masuk is not None and ab.pulang is not None) or (ab.masuk_b is not None and ab.pulang_b is not None):
                                    if geseroff_db.objects.using(req.session["ccabang"]).using(req.session["ccabang"]).filter(dari_tgl=ab.tgl_absen, pegawai_id=ab.pegawai_id).exists():
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
                                            ).save(using=req.session["ccabang"])
                                            
                                            ab.insentif = l['insentif_karyawan']
                                            ab.save(using=req.session["ccabang"])
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
                    ab.save(using=req.session["ccabang"])
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
                            ab.save(using=req.session["ccabang"])
                        # jika jam kerja lebih dari 4 jam
                        else:
                            cuti_db.objects.using(req.session["ccabang"]).get(id=int(c['id'])).delete()
                            pg = pegawai_db.objects.using(req.session["ccabang"]).get(pk=ab.pegawai_id)
                            sc = pg.sisa_cuti
                            ab.keterangan_absensi = ""
                            ab.save(using=req.session["ccabang"])
                            pg.sisa_cuti = sc + 1
                            pg.save(using=req.session["ccabang"])          
                    else:
                        ab.keterangan_absensi = c['keterangan']
                        ab.save(using=req.session["ccabang"])
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
                        ab.save(using=req.session["ccabang"])
                    # jika ada geser off dan dia masuk
                    else:
                        geseroff_db.objects.using(req.session["ccabang"]).get(id=int(g['id'])).delete()    
                else:
                    pass
        
        # opg
        for o in opg:
            if a.pegawai_id == o['idp']:
                # cek jika di dalam data opg diambil pada tanggal saat ini
                if o['diambil_tgl'] == ab.tgl_absen:
                    
                    opg = opg_db.objects.using(req.session["ccabang"]).get(id=o['id'])
                    # jika tidak masuk dan tidak ada pulang
                    if ab.masuk is None and ab.pulang is None and ab.masuk_b is None and ab.pulang_b is None:
                        topg = datetime.strftime(o['diambil_tgl'], '%d-%m-%Y')
                        ab.keterangan_absensi = f'OPG-({topg})'
                        ab.save(using=req.session["ccabang"])                                
                        
                        opg.status = 1
                        opg.edit_by ='Program'
                        opg.save(using=req.session["ccabang"])
                    # jika masuk dan pulang
                    else:
                        opg.diambil_tgl = None
                        opg.edit_by = 'Program'
                        opg.save(using=req.session["ccabang"])
                            
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
                    ab.save(using=req.session["ccabang"])
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
        ab.save(using=req.session["ccabang"])
                    

    return redirect ('absensi',sid=int(sid))   
    # return render(req,'hrd_app/example/ex.html')

@login_required
def detail_absensi(r,userid,tgl,sid):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses

        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)
        divisi = [div.divisi for div in aksesdivisi]

        dsid = dakses.sid_id  

        pgw = pegawai_db.objects.using(r.session["ccabang"]).filter(userid=userid,divisi__in=divisi)
        if not pgw.exists():
            messages.error(r,"Anda tidak memiliki akses")
            print("OSKOKSDOKDOSKSODK")
            return redirect("pegawai",sid=dsid)
        else:
            pgw = pgw[0]
        # get absensi
        ab = absensi_db.objects.using(r.session["ccabang"]).get(pegawai__userid=userid,tgl_absen=tgl)

        # get all jam kerja 

        # dt_raw = sorted(draw,key=lambda i: i["jam_absen"])
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
                "hari":k.hari
            }
            dt_kk.append(obj)

        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
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
                'dsid': dsid,
                'sid': sid,
                'sil': sid_lembur,
                "pegawai":pgw,
                'userid':pgw.userid,
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
    
@login_required
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
    
@login_required
def get_raw_json(r):

        # get raw data absensi
    userid = r.POST.get('userid')
    tgl = datetime.strptime(r.POST.get('tgl'),"%Y-%m-%d")
    tmin = tgl - timedelta(days=1)
    tplus = tgl + timedelta(days=1)
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
    

@login_required
def hapus_jam(r):
    if r.headers['x-requested-with'] == 'XMLHttpRequest':
        id = r.POST.get('id')
        if id is not None:
            data_trans_db.objects.using(r.session["ccabang"]).get(pk=int(id)).delete()
        else:
            pass
    return JsonResponse({"ok":"ok"})

@login_required
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
    
@login_required
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

@login_required
def pu(r,tgl,userid,sid):
    dt = data_trans_db.objects.using(r.session["ccabang"]).filter(jam_absen__date=tgl,userid=userid).order_by('jam_absen')
    id_user = r.user.id
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    abs = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").filter(tgl_absen=tgl,pegawai__userid=userid,pegawai__divisi__in=divisi)
    if not abs.exists():
        messages.error(r,"Anda tidak memiliki akses")
        return redirect("absensi",sid=sid)
    else:
        abs = abs[0]
    abs.masuk = None
    abs.pulang = None
    abs.istirahat = None
    abs.kembali = None
    abs.pulang = None
    abs.masuk_b = None
    abs.istirahat_b = None
    abs.kembali_b = None
    abs.pulang_b = None
    abs.istirahat2 = None
    abs.istirahat2_b = None
    abs.kembali2 = None
    abs.kembali2_b = None
    for d in dt:
        if d.punch == 0:
            abs.masuk = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 1:
            abs.pulang = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 2:
            abs.istirahat = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 3:
            abs.kembali = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 4:
            abs.istirahat2 = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 5:
            abs.kembali2 = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 6:
            abs.masuk = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 7:
            abs.pulang = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 8:
            abs.istirahat = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 9:
            abs.kembali = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 10:
            abs.masuk_b = d.jam_absen.time().strftime('%H:%M:%S') 
        elif d.punch == 11:
            abs.pulang_b = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 12:
            abs.istirahat_b = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 13:
            abs.kembali_b = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 14:
            abs.istirahat2_b = d.jam_absen.time().strftime('%H:%M:%S')
        elif d.punch == 15:
            abs.kembali2_b = d.jam_absen.time().strftime('%H:%M:%S')
        if abs.masuk is not None and abs.pulang is not None:
            if abs.pulang > abs.masuk:
                dmsk = f'{abs.tgl_absen} {abs.masuk}'
                dplg = f'{abs.tgl_absen} {abs.pulang}'
                
                msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                
                dselisih = plg - msk
                djam_selisih = f'{abs.tgl_absen} {dselisih}'
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
                
                tplus = abs.tgl_absen        
                
                dmsk = f'{abs.tgl_absen} {abs.masuk}'
                dplg = f'{tplus} {abs.pulang}'
                
                msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                
                dselisih = plg - msk
                djam_selisih = f'{abs.tgl_absen} {dselisih}'
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
                    tjk = jam                
        else:
            tjk=0

            
        if abs.masuk_b is not None and abs.pulang_b is not None:
            if abs.pulang_b > abs.masuk_b:
                
                dmsk_b = f'{abs.tgl_absen} {abs.masuk_b}'
                dplg_b = f'{abs.tgl_absen} {abs.pulang_b}'
                
                msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
                plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_b = plg_b - msk_b
                djam_selisih_b = f'{abs.tgl_absen} {dselisih_b}'
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
                
                tplus_b = abs.tgl_absen
                dmsk_b = f'{abs.tgl_absen} {abs.masuk_b}'
                dplg_b = f'{tplus_b} {abs.pulang_b}'
                
                msk_b = datetime.strptime(dmsk_b, '%Y-%m-%d %H:%M:%S')
                plg_b = datetime.strptime(dplg_b, '%Y-%m-%d %H:%M:%S')
                dselisih_b = plg_b - msk_b
                # if dselisih_b.hour < 10
                djam_selisih_b = f'{abs.tgl_absen} {dselisih_b}'
                # Split the string to separate the date and time parts
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
        if abs.istirahat is not None and abs.kembali is not None:
            if abs.kembali > abs.istirahat:
                
                dist = f'{abs.tgl_absen} {abs.istirahat}'
                dkmb = f'{abs.tgl_absen} {abs.kembali}'
                
                ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
                kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i = kmb - ist
                djam_selisih_i = f'{abs.tgl_absen} {dselisih_i}'
                selisih_i = datetime.strptime(djam_selisih_i, '%Y-%m-%d %H:%M:%S')
                    
                detik_i = selisih_i.second / 3600
                menit_i = selisih_i.minute / 60
                hour_i = selisih_i.hour
                
                jam_i = int(hour_i) + float(menit_i) + float(detik_i)
                
                tji = jam_i                   
            else:
                
                tplus = abs.tgl_absen + timedelta(days=1)
                
                dist = f'{abs.tgl_absen} {abs.istirahat}'
                dkmb = f'{tplus} {abs.kembali}'
                
                ist = datetime.strptime(dist, '%Y-%m-%d %H:%M:%S')
                kmb = datetime.strptime(dkmb, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i = kmb - ist
                djam_selisih_i = f'{abs.tgl_absen} {dselisih_i}'
                selisih_i = datetime.strptime(djam_selisih_i, '%Y-%m-%d %H:%M:%S')
                    
                detik_i = selisih_i.second / 3600
                menit_i = selisih_i.minute / 60
                hour_i = selisih_i.hour
                
                jam_i = int(hour_i) + float(menit_i) + float(detik_i)
                
                tji = jam_i                      
        else:
            tji = 0        
                
        if abs.istirahat_b is not None and abs.kembali_b is not None:
            if abs.kembali_b > abs.istirahat_b:
                
                dist_b = f'{abs.tgl_absen} {abs.istirahat_b}'
                dkmb_b = f'{abs.tgl_absen} {abs.kembali_b}'
                
                ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
                kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i_b = kmb_b - ist_b
                djam_selisih_i_b = f'{abs.tgl_absen} {dselisih_i_b}'
                selisih_i_b = datetime.strptime(djam_selisih_i_b, '%Y-%m-%d %H:%M:%S')
                    
                detik_i_b = selisih_i_b.second / 3600
                menit_i_b = selisih_i_b.minute / 60
                hour_i_b = selisih_i_b.hour
                
                jam_i_b = int(hour_i_b) + float(menit_i_b) + float(detik_i_b)
                
                tji_b = jam_i_b                   
            else:
                if int(abs.pegawai.status.id) == 3:
                    tplus_b = abs.tgl_absen + timedelta(days=1)
                else:
                    tplus_b = abs.tgl_absen
                dist_b = f'{abs.tgl_absen} {abs.istirahat_b}'
                dkmb_b = f'{tplus_b} {abs.kembali_b}'
                
                ist_b = datetime.strptime(dist_b, '%Y-%m-%d %H:%M:%S')
                kmb_b = datetime.strptime(dkmb_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i_b = kmb_b - ist_b
                djam_selisih_i_b = f'{abs.tgl_absen} {dselisih_i_b}'
                selisih_i_b = datetime.strptime(djam_selisih_i_b, '%Y-%m-%d %H:%M:%S')
                    
                detik_i_b = selisih_i_b.second / 3600
                menit_i_b = selisih_i_b.minute / 60
                hour_i_b = selisih_i_b.hour
                
                jam_i_b = int(hour_i_b) + float(menit_i_b) + float(detik_i_b)
                
                tji_b = jam_i_b                      
        else:
            tji_b = 0        
        
        # total jam istirahat2
        if abs.istirahat2 is not None and abs.kembali2 is not None:
            if abs.kembali2 > abs.istirahat2:
                
                dist2 = f'{abs.tgl_absen} {abs.istirahat2}'
                dkmb2 = f'{abs.tgl_absen} {abs.kembali2}'
                
                ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
                kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i2 = kmb2 - ist2
                djam_selisih_i2 = f'{abs.tgl_absen} {dselisih_i2}'
                selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                    
                detik_i2 = selisih_i2.second / 3600
                menit_i2 = selisih_i2.minute / 60
                hour_i2 = selisih_i2.hour
                
                jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
                
                tji2 = jam_i2                   
            else:
                
                tplus = abs.tgl_absen + timedelta(days=1)
                
                dist2 = f'{abs.tgl_absen} {abs.istirahat2}'
                dkmb2 = f'{tplus} {abs.kembali2}'
                
                ist2 = datetime.strptime(dist2, '%Y-%m-%d %H:%M:%S')
                kmb2 = datetime.strptime(dkmb2, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i2 = kmb2 - ist2
                djam_selisih_i2 = f'{abs.tgl_absen} {dselisih_i2}'
                selisih_i2 = datetime.strptime(djam_selisih_i2, '%Y-%m-%d %H:%M:%S')
                    
                detik_i2 = selisih_i2.second / 3600
                menit_i2 = selisih_i2.minute / 60
                hour_i2 = selisih_i2.hour
                
                jam_i2 = int(hour_i2) + float(menit_i2) + float(detik_i2)
                
                tji2 = jam_i2
        else:
            tji2 = 0   
        if abs.istirahat2_b is not None and abs.kembali2_b is not None:
            if abs.kembali2_b > abs.istirahat2_b:
                
                dist2_b = f'{abs.tgl_absen} {abs.istirahat2_b}'
                dkmb2_b = f'{abs.tgl_absen} {abs.kembali2_b}'
                
                ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
                kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i2_b = kmb2_b - ist2_b
                djam_selisih_i2_b = f'{abs.tgl_absen} {dselisih_i2_b}'
                selisih_i2_b = datetime.strptime(djam_selisih_i2_b, '%Y-%m-%d %H:%M:%S')
                    
                detik_i2_b = selisih_i2_b.second / 3600
                menit_i2_b = selisih_i2_b.minute / 60
                hour_i2_b = selisih_i2_b.hour
                
                jam_i2_b = int(hour_i2_b) + float(menit_i2_b) + float(detik_i2_b)
                
                tji2_b = jam_i2_b                   
            else:
                
                if int(abs.pegawai.status.id) == 3:
                    tplus_b = abs.tgl_absen + timedelta(days=1)
                else:
                    tplus_b = abs.tgl_absen
                
                dist2_b = f'{abs.tgl_absen} {abs.istirahat2_b}'
                dkmb2_b = f'{tplus_b} {abs.kembali2_b}'
                
                ist2_b = datetime.strptime(dist2_b, '%Y-%m-%d %H:%M:%S')
                kmb2_b = datetime.strptime(dkmb2_b, '%Y-%m-%d %H:%M:%S')
                
                dselisih_i2_b = kmb2_b - ist2_b
                djam_selisih_i2_b = f'{abs.tgl_absen} {dselisih_i2_b}'
                selisih_i2 = datetime.strptime(djam_selisih_i2_b, '%Y-%m-%d %H:%M:%S')
                    
                detik_i2_b = selisih_i2_b.second / 3600
                menit_i2_b = selisih_i2_b.minute / 60
                hour_i2_b = selisih_i2_b.hour
                
                jam_i2_b = int(hour_i2_b) + float(menit_i2_b) + float(detik_i2_b)
                
                tji2_b = jam_i2_b
        else:
            tji2_b = 0    
        abs.total_jam_kerja = tjk + tjk_b
        abs.total_jam_istirahat = tji + tji_b
        abs.total_jam_istirahat2 = tji2 + tji2_b
    obj = {
        "id":abs.pk,
        "total_jam_kerja":str(abs.total_jam_kerja),
        "total_jam_istirahat":str(abs.total_jam_istirahat),
        "total_jam_istirahat2":str(abs.total_jam_istirahat2),
        "masuk":str(abs.masuk),
        "pulang":str(abs.pulang),
        "istirahat":str(abs.istirahat),
        "kembali":str(abs.kembali),
        "masuk_b":str(abs.masuk_b),
        "pulang_b":str(abs.pulang_b),
        "istirahat_b":str(abs.istirahat_b),
        "kembali_b":str(abs.kembali_b),
        "istirahat2":str(abs.istirahat2),
        "istirahat2_b":str(abs.istirahat2_b),
        "kembali2":str(abs.kembali2),
        "kembali2_b":str(abs.kembali2_b),
        "tgl_absen":str(abs.tgl_absen),
        "keterangan_absensi":str(abs.keterangan_absensi),
        "keterangan_ijin":str(abs.keterangan_ijin),
        "pegawai":str(abs.pegawai.userid),
        "keterangan_lain":str(abs.keterangan_lain),
        "libur_nasional":str(abs.libur_nasional),
        "lama_istirahat":str(abs.lama_istirahat),
        "lama_istirahat2":str(abs.lama_istirahat2),
        "jam_masuk":str(abs.jam_masuk),
        "jam_pulang":str(abs.jam_pulang),
        "lebih_jam_kerja":str(abs.lebih_jam_kerja),
    }
    abs.save(using=r.session["ccabang"])
    return redirect("dabsen",userid=userid,tgl=tgl,sid=sid)

@login_required
def edit_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")
    ket = r.POST.get("ket")
    id = r.POST.get("id")
    sid = r.POST.get("sid")
    id_user = r.user.id
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    print(jenis_ijin,ket,id,sid)
    if jenis_ijin_db.objects.using(r.session["ccabang"]).filter(pk=int(jenis_ijin)).exists():
        if absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").filter(pk=int(id),pegawai__divisi__in=divisi).exists():
            ji = jenis_ijin_db.objects.using(r.session["ccabang"]).get(pk=int(jenis_ijin))
            ab = absensi_db.objects.using(r.session["ccabang"]).get(pk=int(id))
            print(ab)
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

@login_required
def edit_jamkerja(r,userid,tgl,sid):
    masuk = r.POST.get("jam_masuk")
    keluar = r.POST.get("jam_keluar")
    lama_ist = r.POST.get("lama_istirahat")
    id = r.POST.get("id")
    if masuk == '' or keluar == "" or lama_ist == "":
        messages.add_message(r,messages.ERROR,"Form harus lengkap")
        return redirect("dabsen",userid=userid,tgl=tgl,sid=sid)
    id_user = r.user.id
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
    return redirect("dabsen",userid=userid,tgl=tgl,sid=sid)


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