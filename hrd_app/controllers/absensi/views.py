from hrd_app.controllers.lib import *
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
        jenis_ijin = jenis_ijin_db.objects.all()   
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
            'jenis_ijin' : jenis_ijin,
            'modul_aktif' : 'Absensi'
        }
        
        return render(request,'hrd_app/absensi/absensi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_absensi(request):
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        sid = request.POST.get('sid')
        dari = datetime.strptime(request.POST.get('ctgl1'),'%d-%m-%Y').date()
        sampai = datetime.strptime(request.POST.get('ctgl2'),'%d-%m-%Y').date()
        
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
                    
                if ab.masuk is not None:
                    msk = f"{ab.masuk}"
                else:
                    msk = None

                if ab.pulang is not None:
                    plg = f"{ab.pulang}"
                else:
                    plg = None

                if ab.masuk_b is not None:
                    msk_b = f"{ab.masuk_b}"
                else:
                    msk_b = None

                if ab.pulang_b is not None:
                    plg_b = f"{ab.pulang_b}"
                else:
                    plg_b = None

                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = ""    

                if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                    ist_b += f" {ab.istirahat_b} / {ab.istirahat2_b})"
                elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                    ist_b += f" {ab.istirahat_b}"
                elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                    ist_b += f" {ab.istirahat2_b}"
                else:
                    ist_b = ""
            
                    
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{ab.kembali} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:                  
                    kmb = f'{ab.kembali}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{ab.kembali2}'    
                else:
                    kmb = ""        

                if ab.kembali_b is not None and ab.kembali2_b is not None:
                    kmb_b += f" {ab.kembali_b} / {ab.kembali2_b})"
                elif ab.kembali_b is not None and ab.kembali2_b is None:
                    kmb_b += f" {ab.kembali_b}"
                elif ab.kembali_b is None and ab.kembali2_b is not None:
                    kmb_b += f" {ab.kembali2_b}"
                else:
                    kmb_b = "" 
                

                if ab.keterangan_absensi is not None:
                    sket += f'{ab.keterangan_absensi}, '                 
                if ab.keterangan_ijin is not None:
                    sket += f'{ab.keterangan_ijin}, '
                    kijin = ''
                else:
                    if ab.masuk is not None and ab.jam_masuk is not None:
                        if ab.masuk > ab.jam_masuk:
                            sket += f"Terlambat masuk tanpa ijin, "                
                if ab.keterangan_lain is not None:
                    sket += f'{ab.keterangan_lain}, '                    
                if ab.libur_nasional is not None:
                    sket += f'{ab.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if ab.istirahat is not None and ab.lama_istirahat is not None:
                    jmkem = datetime.combine(ab.tgl_absen,ab.jam_istirahat) + timedelta(minutes=float(ab.lama_istirahat) * 60) + timedelta(minutes=5)
                    jmkem = jmkem.time()
                else:
                    jmkem = None
                absen = {
                    'id': ab.id,
                    'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    "tgl_absen":ab.tgl_absen,
                    'nama': ab.pegawai.nama,
                    'nik': ab.pegawai.nik,
                    'userid': ab.pegawai.userid,
                    'bagian': bagian,
                    "jam_masuk":ab.jam_masuk,
                    "jam_pulang":ab.jam_pulang,
                    'masuk': msk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': plg,
                    'masuk_b': msk_b,
                    'keluar_b': ist_b,
                    'kembali_b': kmb_b,
                    'pulang_b': plg_b,
                    "jam_kembali":jmkem,
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
                    
                if ab.masuk is not None:
                    msk = f"{ab.masuk}"
                else:
                    msk = None

                if ab.pulang is not None:
                    plg = f"{ab.pulang}"
                else:
                    plg = None

                if ab.masuk_b is not None:
                    msk_b = f"{ab.masuk_b}"
                else:
                    msk_b = None

                if ab.pulang_b is not None:
                    plg_b = f"{ab.pulang_b}"
                else:
                    plg_b = None

                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = ""    

                if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                    ist_b += f" {ab.istirahat_b} / {ab.istirahat2_b})"
                elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                    ist_b += f" {ab.istirahat_b}"
                elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                    ist_b += f" {ab.istirahat2_b}"
                else:
                    ist_b = ""
            
                    
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{ab.kembali} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:                  
                    kmb = f'{ab.kembali}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{ab.kembali2}'    
                else:
                    kmb = ""        

                if ab.kembali_b is not None and ab.kembali2_b is not None:
                    kmb_b += f" {ab.kembali_b} / {ab.kembali2_b})"
                elif ab.kembali_b is not None and ab.kembali2_b is None:
                    kmb_b += f" {ab.kembali_b}"
                elif ab.kembali_b is None and ab.kembali2_b is not None:
                    kmb_b += f" {ab.kembali2_b}"
                else:
                    kmb_b = "" 
                

                if ab.keterangan_absensi is not None:
                    sket += f'{ab.keterangan_absensi}, '                 
                if ab.keterangan_ijin is not None:
                    sket += f'{ab.keterangan_ijin}, '
                    kijin = ''
                else:
                    if ab.masuk is not None and ab.jam_masuk is not None:
                        if ab.masuk > ab.jam_masuk:
                            sket += f"Terlambat masuk tanpa ijin, "                
                if ab.keterangan_lain is not None:
                    sket += f'{ab.keterangan_lain}, '                    
                if ab.libur_nasional is not None:
                    sket += f'{ab.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if ab.istirahat is not None and ab.lama_istirahat is not None:
                    jmkem = datetime.combine(ab.tgl_absen,ab.jam_istirahat) + timedelta(minutes=float(ab.lama_istirahat) * 60) + timedelta(minutes=5)
                    jmkem = jmkem.time()
                else:
                    jmkem = None
                absen = {
                    'id': ab.id,
                    'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    "tgl_absen":ab.tgl_absen,
                    'nama': ab.pegawai.nama,
                    'nik': ab.pegawai.nik,
                    'userid': ab.pegawai.userid,
                    'bagian': bagian,
                    "jam_masuk":ab.jam_masuk,
                    "jam_pulang":ab.jam_pulang,
                    'masuk': msk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': plg,
                    'masuk_b': msk_b,
                    'keluar_b': ist_b,
                    'kembali_b': kmb_b,
                    'pulang_b': plg_b,
                    "jam_kembali":jmkem,
                    'tj': ab.total_jam_kerja,
                    'ket': sket,
                    'sln': sln,
                    'ln': ab.libur_nasional
                }

                data.append(absen)
        return JsonResponse({"data": data })


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
                    
                if ab.masuk is not None:
                    msk = f"{ab.masuk}"
                else:
                    msk = None

                if ab.pulang is not None:
                    plg = f"{ab.pulang}"
                else:
                    plg = None

                if ab.masuk_b is not None:
                    msk_b = f"{ab.masuk_b}"
                else:
                    msk_b = None

                if ab.pulang_b is not None:
                    plg_b = f"{ab.pulang_b}"
                else:
                    plg_b = None

                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = ""    

                if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                    ist_b += f" {ab.istirahat_b} / {ab.istirahat2_b})"
                elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                    ist_b += f" {ab.istirahat_b}"
                elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                    ist_b += f" {ab.istirahat2_b}"
                else:
                    ist_b = ""
            
                    
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{ab.kembali} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:                  
                    kmb = f'{ab.kembali}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{ab.kembali2}'    
                else:
                    kmb = ""        

                if ab.kembali_b is not None and ab.kembali2_b is not None:
                    kmb_b += f" {ab.kembali_b} / {ab.kembali2_b})"
                elif ab.kembali_b is not None and ab.kembali2_b is None:
                    kmb_b += f" {ab.kembali_b}"
                elif ab.kembali_b is None and ab.kembali2_b is not None:
                    kmb_b += f" {ab.kembali2_b}"
                else:
                    kmb_b = "" 
                

                if ab.keterangan_absensi is not None:
                    sket += f'{ab.keterangan_absensi}, '                 
                if ab.keterangan_ijin is not None:
                    sket += f'{ab.keterangan_ijin}, '
                    kijin = ''
                else:
                    if ab.masuk is not None and ab.jam_masuk is not None:
                        if ab.masuk > ab.jam_masuk:
                            sket += f"Terlambat masuk tanpa ijin, "

                if ab.keterangan_lain is not None:
                    sket += f'{ab.keterangan_lain}, '                    
                if ab.libur_nasional is not None:
                    sket += f'{ab.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if ab.istirahat is not None and ab.lama_istirahat is not None:
                    jmkem = datetime.combine(ab.tgl_absen,ab.jam_istirahat) + timedelta(minutes=float(ab.lama_istirahat) * 60) + timedelta(minutes=5)
                    jmkem = jmkem.time()
                else:
                    jmkem = None
                absen = {
                    'id': ab.id,
                    'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    "tgl_absen":ab.tgl_absen,
                    'nama': ab.pegawai.nama,
                    'nik': ab.pegawai.nik,
                    'userid': ab.pegawai.userid,
                    'bagian': bagian,
                    "jam_masuk":ab.jam_masuk,
                    "jam_pulang":ab.jam_pulang,
                    'masuk': msk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': plg,
                    'masuk_b': msk_b,
                    'keluar_b': ist_b,
                    'kembali_b': kmb_b,
                    'pulang_b': plg_b,
                    "jam_kembali":jmkem,
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
                    
                if ab.masuk is not None:
                    msk = f"{ab.masuk}"
                else:
                    msk = None

                if ab.pulang is not None:
                    plg = f"{ab.pulang}"
                else:
                    plg = None

                if ab.masuk_b is not None:
                    msk_b = f"{ab.masuk_b}"
                else:
                    msk_b = None

                if ab.pulang_b is not None:
                    plg_b = f"{ab.pulang_b}"
                else:
                    plg_b = None

                if ab.istirahat is not None and ab.istirahat2 is not None:
                    ist = f'{ab.istirahat} / {ab.istirahat2}'
                elif ab.istirahat is not None and ab.istirahat2 is None:                  
                    ist = f'{ab.istirahat}'
                elif ab.istirahat is None and ab.istirahat2 is not None:                  
                    ist = f'{ab.istirahat2}'
                else:
                    ist = ""    

                if ab.istirahat_b is not None and ab.istirahat2_b is not None:
                    ist_b += f" {ab.istirahat_b} / {ab.istirahat2_b})"
                elif ab.istirahat_b is not None and ab.istirahat2_b is None:
                    ist_b += f" {ab.istirahat_b}"
                elif ab.istirahat_b is None and ab.istirahat2_b is not None:
                    ist_b += f" {ab.istirahat2_b}"
                else:
                    ist_b = ""
            
                    
                if ab.kembali is not None and ab.kembali2 is not None:
                    kmb = f'{ab.kembali} / {ab.kembali2}'
                elif ab.kembali is not None and ab.kembali2 is None:                  
                    kmb = f'{ab.kembali}'
                elif ab.kembali is None and ab.kembali2 is not None:                  
                    kmb = f'{ab.kembali2}'    
                else:
                    kmb = ""        

                if ab.kembali_b is not None and ab.kembali2_b is not None:
                    kmb_b += f" {ab.kembali_b} / {ab.kembali2_b})"
                elif ab.kembali_b is not None and ab.kembali2_b is None:
                    kmb_b += f" {ab.kembali_b}"
                elif ab.kembali_b is None and ab.kembali2_b is not None:
                    kmb_b += f" {ab.kembali2_b}"
                else:
                    kmb_b = "" 
                

                if ab.keterangan_absensi is not None:
                    sket += f'{ab.keterangan_absensi}, '                 
                if ab.keterangan_ijin is not None:
                    sket += f'{ab.keterangan_ijin}, '
                    kijin = ''
                else:
                    if ab.masuk is not None and ab.jam_masuk is not None:
                        if ab.masuk > ab.jam_masuk:
                            sket += f"Terlambat masuk tanpa ijin, "
                if ab.keterangan_lain is not None:
                    sket += f'{ab.keterangan_lain}, '                    
                if ab.libur_nasional is not None:
                    sket += f'{ab.libur_nasional}, '
                    sln = 1
                else:
                    sln = 0          

                if ab.istirahat is not None and ab.lama_istirahat is not None:
                    jmkem = datetime.combine(ab.tgl_absen,ab.jam_istirahat) + timedelta(minutes=float(ab.lama_istirahat) * 60) + timedelta(minutes=5)
                    jmkem = jmkem.time()
                else:
                    jmkem = None
                absen = {
                    'id': ab.id,
                    'tgl': datetime.strftime(ab.tgl_absen,'%d-%m-%Y'),
                    'hari': hari_ini,
                    "tgl_absen":ab.tgl_absen,
                    'nama': ab.pegawai.nama,
                    'nik': ab.pegawai.nik,
                    'userid': ab.pegawai.userid,
                    'bagian': bagian,
                    "jam_masuk":ab.jam_masuk,
                    "jam_pulang":ab.jam_pulang,
                    'masuk': msk,
                    'keluar': ist,
                    'kembali': kmb,
                    'pulang': plg,
                    'masuk_b': msk_b,
                    'keluar_b': ist_b,
                    'kembali_b': kmb_b,
                    'pulang_b': plg_b,
                    "jam_kembali":jmkem,
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
    att = sorted(dmesin, key=lambda i: i['jam_absen'])

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
                        bb_msk = jam_absen - timedelta(hours=4)
                        ba_msk = jam_absen + timedelta(hours=4)
                        jk = None
                        if a["punch"] == 0:
                            jk = jamkerja_db.objects.filter(kk_id=ab.pegawai.kelompok_kerja.pk,jam_masuk__gte=bb_msk.time(),jam_masuk__lte=ba_msk.time())
                            i = 0
                            print(jk,"JK")
                            if len(jk) > 1: 
                                for j in jk:
                                    try:
                                        plus = jk[i+1]
                                    except:
                                        break
                                    selisih = abs(datetime.combine(ab.tgl_absen,j.jam_masuk) - datetime.combine(ab.tgl_absen,plus.jam_masuk))
                                    selisih = selisih.total_seconds() / 60 / 2
                                    j_1 = datetime.combine(ab.tgl_absen,j.jam_masuk) + timedelta(minutes=selisih)
                                    j_2 = datetime.combine(ab.tgl_absen,j.jam_masuk) - timedelta(minutes=selisih)
                                    jk_1 = datetime.combine(ab.tgl_absen,plus.jam_masuk) + timedelta(minutes=selisih)
                                    jk_2 = datetime.combine(ab.tgl_absen,plus.jam_masuk) - timedelta(minutes=selisih)
                                    if jam_absen.time() < j_1.time() and jam_absen.time() > j_2.time():
                                        ab.jam_masuk = j.jam_masuk
                                        ab.jam_istirahat = j.jam_istirahat
                                        ab.jam_pulang = j.jam_pulang
                                        ist = datetime.combine(ab.tgl_absen, j.jam_istirahat) - datetime.combine(ab.tgl_absen, j.jam_kembali_istirahat)
                                        ist2 = datetime.combine(ab.tgl_absen, j.jam_istirahat2) - datetime.combine(ab.tgl_absen, j.jam_kembali_istirahat2)
                                        ist = abs(ist.total_seconds() / 3600)
                                        ist2 = abs(ist2.total_seconds() / 3600)
                                        ab.lama_istirahat = ist
                                        ab.lama_istirahat2 = ist2
                                    elif jam_absen.time() < jk_1.time() and jam_absen.time() > jk_2.time():
                                        ab.jam_masuk = plus.jam_masuk
                                        ab.jam_istirahat = plus.jam_istirahat
                                        ab.jam_pulang = plus.jam_pulang
                                        ist = datetime.combine(ab.tgl_absen, plus.jam_istirahat) - datetime.combine(ab.tgl_absen, plus.jam_kembali_istirahat)
                                        ist2 = datetime.combine(ab.tgl_absen, plus.jam_istirahat2) - datetime.combine(ab.tgl_absen, plus.jam_kembali_istirahat2)
                                        ist = abs(ist.total_seconds() / 3600)
                                        ist2 = abs(ist2.total_seconds() / 3600)
                                        ab.lama_istirahat = ist
                                        ab.lama_istirahat2 = ist2
                            elif len(jk) == 1:
                                ab.jam_masuk = jk[0].jam_masuk
                                ab.jam_istirahat = jk[0].jam_istirahat
                                ab.jam_pulang = jk[0].jam_pulang
                                ist = datetime.combine(ab.tgl_absen, jk[0].jam_istirahat) - datetime.combine(ab.tgl_absen, jk[0].jam_kembali_istirahat)
                                ist2 = datetime.combine(ab.tgl_absen, jk[0].jam_istirahat2) - datetime.combine(ab.tgl_absen, jk[0].jam_kembali_istirahat2)
                                ist = abs(ist.total_seconds() / 3600)
                                ist2 = abs(ist2.total_seconds() / 3600)
                                ab.lama_istirahat = ist
                                ab.lama_istirahat2 = ist2
                                
# ++++++++++++++++++++++++++++++++++++++++  MASUK  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        if a["punch"] == 0 and jam_absen.hour > 4 and jam_absen.hour < 18 :
                            if ab.masuk is not None:
                                if ab.masuk.hour > 18:
                                    ab.masuk_b = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 10,
                                        "mesin": a["mesin"],
                                        "ket": "Masuk B"
                                    }
                                    dt.append(data)
                                else:
                                    s = jam_absen - datetime.combine(ab.tgl_absen,ab.masuk)
                                    if s.total_seconds() / 3600 > 4:
                                        ab.masuk_b = jam_absen.time()
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 10,
                                            "mesin": a["mesin"],
                                            "ket": "Masuk B"
                                        }
                                        dt.append(data)
                                    else:
                                        ab.masuk = jam_absen.time()
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": a["punch"],
                                            "mesin": a["mesin"],
                                            "ket": "Masuk"
                                        }
                                        dt.append(data)
                            elif ab.pulang is not None or ab.istirahat is not None or ab.kembali is not None:
                                ab.masuk_b = jam_absen.time()
                                ab.save()
                                data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 10,
                                        "mesin": a["mesin"],
                                        "ket": "Masuk B"
                                }
                                dt.append(data)
                            else:
                                ab.masuk = jam_absen.time()
                                ab.save()
                                data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": a["punch"],
                                        "mesin": a["mesin"],
                                        "ket": "Masuk"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  MASUK MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 0 and jam_absen.hour > 18:
                            # pastikan untuk userid hotel
                            if pg is not None:
                                if pg["status_id"] == 3:
                                    ab2 = absensi_db.objects.get(tgl_absen=tplus.date(),pegawai__userid=a["userid"])
                                    if ab.masuk is not None:
                                        if ab.masuk.hour > 18:
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen + timedelta(days=1),
                                                "punch": 6,
                                                "mesin": a["mesin"],
                                                "ket": "Masuk Malam"
                                            }
                                            dt.append(data)
                                        else:
                                            if ab2.masuk is not None:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.masuk = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                    elif ab.istirahat is not None:
                                        if ab.istirahat.hour < 9:
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen + timedelta(days=1),
                                                "punch": 6,
                                                "mesin": a["mesin"],
                                                "ket": "Masuk Malam"
                                            }
                                            dt.append(data)
                                        else:
                                            if ab2.masuk is not None:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.masuk = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                    elif ab.kembali is not None:
                                        if ab.kembali.hour < 9:
                                            pass
                                        else:
                                            if ab2.masuk is not None:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                    elif ab.pulang is not None:
                                        if ab.pulang.hour < 9:
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen + timedelta(days=1),
                                                "punch": 6,
                                                "mesin": a["mesin"],
                                                "ket": "Masuk Malam"
                                            }
                                            dt.append(data)
                                        else:
                                            if ab2.masuk is not None:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.masuk = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen + timedelta(days=1),
                                                    "punch": 6,
                                                    "mesin": a["mesin"],
                                                    "ket": "Masuk Malam"
                                                }
                                                dt.append(data)
                                    else:
                                        ab2.masuk = jam_absen.time()
                                        ab2.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 6,
                                            "mesin": a["mesin"],
                                            "ket": "Masuk Malam"
                                        }
                                        dt.append(data)
                                else:
                                    if ab.masuk is not None:
                                        d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab.tgl_absen,ab.masuk)
                                        if d.total_seconds() / 3600 > 5:
                                            ab.masuk_b = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 6,
                                                "mesin": a["mesin"],
                                                "ket": "Masuk Malam"
                                            }
                                            dt.append(data)
                                        else:
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen + timedelta(days=1),
                                                "punch": 6,
                                                "mesin": a["mesin"],
                                                "ket": "Masuk Malam"
                                            }
                                            dt.append(data)
                                    elif ab.pulang is not None or ab.istirahat is not None or ab.kembali is not None:
                                        ab.masuk_b = jam_absen.time()
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 6,
                                            "mesin": a["mesin"],
                                            "ket": "Masuk Malam"
                                        }
                                        dt.append(data)
                                    else:
                                        ab.masuk = jam_absen.time()
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 6,
                                            "mesin": a["mesin"],
                                            "ket": "Masuk Malam"
                                        }
                                        dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 2 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                            if ab.istirahat is not None:
                                if (int(jam_absen.hour) - int(ab.istirahat.hour)) > 4:
                                    ab.istirahat_b = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 12,
                                        "mesin": a["mesin"],
                                        "ket": "Istirahat B"
                                    }
                                    dt.append(data)
                                else:
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": a["punch"],
                                        "mesin": a["mesin"],
                                        "ket": "Istirahat"
                                    }
                                    dt.append(data)
                            elif ab.pulang is not None or ab.kembali is not None or ab.masuk_b is not None or ab.masuk is not None:
                                if ab.istirahat is not None:
                                    ab.istirahat_b = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 12,
                                        "mesin": a["mesin"],
                                        "ket": "Istirahat B"
                                    }
                                    dt.append(data)
                                else:
                                    ab.istirahat = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": a["punch"],
                                        "mesin": a["mesin"],
                                        "ket": "Istirahat"
                                    }
                                    dt.append(data)
                            else:
                                ab.istirahat = jam_absen.time()
                                ab.save()
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen,
                                    "punch": a["punch"],
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat"
                                }
                                dt.append(data)
                                        
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM TASIK +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 2 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
                            if int(jam_absen.hour) > 21:
                                if ab.masuk_b is not None:
                                    if int(ab.masuk_b.hour) > 18:
                                        ab.istirahat_b = jam_absen.time()
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 8,
                                            "mesin": a["mesin"],
                                            "ket": "Istirahat Malam"
                                        }
                                        dt.append(data)
                                    else:
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 8,
                                            "mesin": a["mesin"],
                                            "ket": "Istirahat Malam"
                                        }
                                        dt.append(data)
                                else:
                                    if ab.pulang_b is not None:
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 8,
                                            "mesin": a["mesin"],
                                            "ket": "Istirahat Malam"
                                        }
                                        dt.append(data)
                                    else:
                                        ab.istirahat = jam_absen.time()
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 8,
                                            "mesin": a["mesin"],
                                            "ket": "Istirahat Malam"
                                        }
                                        dt.append(data)
                                       

                            elif int(jam_absen.hour) < 8:
                                if pg is not None:
                                    if pg["status_id"] == 3:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.istirahat is not None:
                                                if ab2.istirahat.hour < 9:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab.istirahat = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.masuk is not None:
                                                if ab2.masuk.hour > 18:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab.istirahat = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.kembali is not None:
                                                if ab2.kembali.hour > 9:
                                                    ab.istirahat = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.pulang is not None:
                                                if ab2.pulang.hour > 9:
                                                    ab.istirahat = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                ab2.istirahat = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 8,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat Malam"
                                                }
                                                dt.append(data)
                                        except absensi_db.DoesNotExist:
                                            ab.istirahat = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 8,
                                                "mesin": a["mesin"],
                                                "ket": "Istirahat Malam"
                                            }
                                            dt.append(data)
                                    else:
                                        try:
                                            # tanda
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.istirahat is not None:
                                                if ab2.istirahat.hour < 9:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.istirahat_b = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.kembali is not None:
                                                if ab2.kembali.hour < 9:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.istirahat_b = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.pulang is not None:
                                                if ab2.pulang.hour < 9:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.istirahat_b = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                if ab2.masuk_b is not None:
                                                    if int(ab2.masuk_b.hour) > 18:
                                                        ab2.istirahat_b = jam_absen.time()
                                                        ab2.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen - timedelta(days=1),
                                                            "punch": 8,
                                                            "mesin": a["mesin"],
                                                            "ket": "Istirahat Malam"
                                                        }
                                                        dt.append(data)
                                                    else:
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen - timedelta(days=1),
                                                            "punch": 8,
                                                            "mesin": a["mesin"],
                                                            "ket": "Istirahat Malam"
                                                        }
                                                        dt.append(data)
                                                else:
                                                    ab2.istirahat = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 8,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat Malam"
                                                    }
                                                    dt.append(data)
                                        except absensi_db.DoesNotExist:
                                            ab.istirahat = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 8,
                                                "mesin": a["mesin"],
                                                "ket": "Istirahat Malam"
                                            }
                                            dt.append(data)
                                else:
                                    pass
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 4 and int(jam_absen.hour) > 8 and int(jam_absen.hour) < 21:
                            if ab.istirahat2 is not None:
                                if (int(jam_absen.hour) - int(ab.istirahat2.hour)) > 4:
                                    ab.istirahat2_b = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 14,
                                        "mesin": a["mesin"],
                                        "ket": "Istirahat 2 B"
                                    }
                                    dt.append(data)
                                else:
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": a["punch"],
                                        "mesin": a["mesin"],
                                        "ket": "Istirahat 2"
                                    }
                                    dt.append(data)
                            elif ab.pulang is not None or ab.kembali2 is not None or ab.masuk_b is not None:
                                ab.istirahat2_b = jam_absen.time()
                                ab.save()
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen,
                                    "punch": 14,
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat 2 B"
                                }
                                dt.append(data)
                            else:
                                ab.istirahat2 = jam_absen.time()
                                ab.save()
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen,
                                    "punch": a["punch"],
                                    "mesin": a["mesin"],
                                    "ket": "Istirahat 2"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  ISTIRAHAT MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 4 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 8):
                            if pg is not None:
                                if pg["status_id"] == 3:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
                                            ab.istirahat2 = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 10,
                                                "mesin": a["mesin"],
                                                "ket": "Istirahat 2 Malam"
                                            }
                                            dt.append(data)
                                        else:
                                            pass
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab2.tgl_absen,ab2.istirahat2)
                                            if ab2.istirahat2 is not None:
                                                if ab2.istirahat2 < 9:
                                                    ab2.istirahat2 = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab.istirahat2 = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
                                                    ab.istirahat2 = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.istirahat2 = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.kembali is not None:
                                                if int(ab2.kembali.hour) > 8:
                                                    ab.istirahat2 = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.istirahat2 = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.pulang is not None:
                                                if int(ab2.pulang.hour) < 9:
                                                    ab2.istirahat2 = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab.istirahat2 = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                ab2.istirahat2 = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                        except absensi_db.DoesNotExist:
                                            absensi_db(
                                                tgl_absen=tmin.date(),
                                                pegawai_id=ab.pegawai.pk,
                                                istirahat2=jam_absen.time()
                                            ).save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen - timedelta(days=1),
                                                "punch": 10,
                                                "mesin": a["mesin"],
                                                "ket": "Istirahat 2 Malam"
                                            }
                                            dt.append(data)
                                else:
                                    try:
                                        ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.istirahat2 is not None:
                                            if ab2.istirahat2.hour < 9:
                                                ab2.istirahat2 = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.istirahat2_b = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.kembali is not None:
                                            if ab2.kembali.hour < 9:
                                                ab2.istirahat2 = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.istirahat2_b = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.pulang is not None:
                                            if ab2.pulang.hour < 9:
                                                ab2.istirahat2 = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.istirahat2_b = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                        else:
                                            if ab2.masuk_b is not None:
                                                if int(ab2.masuk_b.hour) > 18:
                                                    ab2.istirahat2_b = jam_absen
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 10,
                                                        "mesin": a["mesin"],
                                                        "ket": "Istirahat 2 Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                ab2.istirahat2 = jam_absen
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 10,
                                                    "mesin": a["mesin"],
                                                    "ket": "Istirahat 2 Malam"
                                                }
                                                dt.append(data)
                                    except absensi_db.DoesNotExist:
                                        absensi_db(
                                            tgl_absen=tmin.date(),
                                            pegawai_id=ab.pegawai.pk,
                                            istirahat2=jam_absen
                                        ).save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen - timedelta(days=1),
                                            "punch": 10,
                                            "mesin": a["mesin"],
                                            "ket": "Istirahat 2 Malam"
                                        }
                                        dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 3 and int(jam_absen.hour) > 9:
                            if ab.kembali is not None:
                                if int(jam_absen.hour) - int(ab.kembali.hour) > 4:
                                    ab.kembali_b = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 13,
                                        "mesin": a["mesin"],
                                        "ket": "Kembali B"
                                    }
                                    dt.append(data)
                                else:
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 3,
                                        "mesin": a["mesin"],
                                        "ket": "Kembali"
                                    }
                                    dt.append(data)
                            elif ab.masuk_b is not None or ab.pulang is not None or ab.istirahat_b is not None:
                                ab.kembali_b = jam_absen.time()
                                ab.save()
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen,
                                    "punch": 13,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali B"
                                }
                                dt.append(data)
                            else:
                                ab.kembali = jam_absen.time()
                                ab.save()
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen,
                                    "punch": 3,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 5 and int(jam_absen.hour) > 9:
                            if ab.kembali2 is not None:
                                if int(jam_absen.hour) - int(ab.kembali2.hour) > 4:
                                    ab.kembali2_b = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 15,
                                        "mesin": a["mesin"],
                                        "ket": "Kembali 2 B"
                                    }
                                    dt.append(data)
                                else:
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 5,
                                        "mesin": a["mesin"],
                                        "ket": "Kembali 2"
                                    }
                                    dt.append(data)
                            elif ab.masuk_b is not None or ab.pulang is not None or ab.istirahat2_b is not None:
                                ab.kembali2_b = jam_absen.time()
                                ab.save()
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen,
                                    "punch": 15,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali 2 B"
                                }
                                dt.append(data)
                            else:
                                ab.kembali2 = jam_absen.time()
                                ab.save()
                                data = {
                                    "userid": a["userid"],
                                    "jam_absen": jam_absen,
                                    "punch": 5,
                                    "mesin": a["mesin"],
                                    "ket": "Kembali 2"
                                }
                                dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI MALAM 2 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 5 and int(jam_absen.hour) < 9:
                            if pg is not None:
                                if pg["status_id"] == 3:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
                                            ab.kembali2 = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 11,
                                                "mesin": a["mesin"],
                                                "ket": "Kembali 2 Malam"
                                            }
                                            dt.append(data)
                                        else:
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 11,
                                                "mesin": a["mesin"],
                                                "ket": "Kembali 2 Malam"
                                            }
                                            dt.append(data)
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab2.tgl_absen,ab2.kembali2)
                                            if ab2.istirahat2 is not None:
                                                if ab2.kembali2.hour < 9:
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab.kembali2 = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
                                                    ab.kembali2 = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.kembali2 is not None:
                                                if int(ab2.kembali2.hour) > 8 and int(ab2.kembali2.hour) < 21:
                                                    ab.kembali2 = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.pulang is not None:
                                                if int(ab2.pulang.hour) > 9:
                                                    ab.kembali2 = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.kembali2 = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                ab2.kembali2 = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali 2 Malam"
                                                }
                                                dt.append(data)
                                        except absensi_db.DoesNotExist:
                                            ab.kembali  = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 11,
                                                "mesin": a["mesin"],
                                                "ket": "Kembali 2 Malam"
                                            }
                                            dt.append(data)
                                else:
                                    try:
                                        ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.kembali2 is not None:
                                            if ab2.kembali2.hour < 9:
                                                ab2.kembali2 = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali 2 Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.kembali2_b = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali 2 Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.pulang is not None:
                                            if ab2.pulang.hour < 9:
                                                ab2.kembali2 = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali 2 Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.kembali2_b = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali 2 Malam"
                                                }
                                                dt.append(data)
                                        else:
                                            if ab2.masuk_b is not None:
                                                if int(ab2.masuk_b.hour) > 18:
                                                    ab2.kembali2_b = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali 2 Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                ab2.kembali2 = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali 2 Malam"
                                                }
                                                dt.append(data)
                                    except absensi_db.DoesNotExist:
                                        ab.kembali2 = jam_absen.time()
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen - timedelta(days=1),
                                            "punch": 11,
                                            "mesin": a["mesin"],
                                            "ket": "Kembali 2 Malam"
                                        }
                                        dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  KEMBALI MALAM +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 3 and (int(jam_absen.hour) > 21 or int(jam_absen.hour) < 9):
                            if int(jam_absen.hour) > 21:
                                if ab.masuk_b is not None:
                                    if int(ab.masuk_b.hour) > 18:
                                        ab.kembali_b = jam_absen
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 11,
                                            "mesin": a["mesin"],
                                            "ket": "Kembali Malam"
                                        }
                                        dt.append(data)
                                    else:
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 11,
                                            "mesin": a["mesin"],
                                            "ket": "Kembali Malam"
                                        }
                                        dt.append(data)
                                else:
                                    if ab.pulang_b is not None:
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 11,
                                            "mesin": a["mesin"],
                                            "ket": "Kembali Malam"
                                        }
                                        dt.append(data)
                                    else:
                                        ab.kembali = jam_absen
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 11,
                                            "mesin": a["mesin"],
                                            "ket": "Kembali Malam"
                                        }
                                        dt.append(data)
                            elif int(jam_absen.hour) < 9:
                                if pg is not None:
                                    if pg["status_id"] == 3:
                                        # hari esok
                                        if ab.masuk is not None:
                                            if int(ab.masuk.hour) > 18:
                                                ab.kembali = jam_absen.time()
                                                ab.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali Malam"
                                                }
                                                dt.append(data)
                                        else:
                                            try:
                                                ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                                if ab2.kembali is not None:
                                                    if ab2.kembali.hour < 9:
                                                        ab2.kembali = jam_absen.time()
                                                        ab2.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen - timedelta(days=1),
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                    else:
                                                        ab.kembali = jam_absen.time()
                                                        ab.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen,
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                elif ab2.masuk is not None:
                                                    if int(ab2.masuk.hour) < 18:
                                                        ab.kembali = jam_absen.time()
                                                        ab.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen,
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                    else:
                                                        ab2.kembali = jam_absen.time()
                                                        ab2.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen - timedelta(days=1),
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                elif ab2.istirahat is not None:
                                                    if ab2.istirahat.hour < 9:
                                                        ab.kembali = jam_absen.time()
                                                        ab.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen,
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                    else:
                                                        ab2.kembali = jam_absen.time()
                                                        ab2.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen - timedelta(days=1),
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                elif ab2.pulang is not None:
                                                    if ab2.pulang.hour < 9:
                                                        ab2.kembali = jam_absen.time()
                                                        ab2.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen - timedelta(days=1),
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                    else:
                                                        ab.kembali = jam_absen.time()
                                                        ab.save()
                                                        data = {
                                                            "userid": a["userid"],
                                                            "jam_absen": jam_absen,
                                                            "punch": 11,
                                                            "mesin": a["mesin"],
                                                            "ket": "Kembali Malam"
                                                        }
                                                        dt.append(data)
                                                else:
                                                    ab2.kembali = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali Malam"
                                                    }
                                                    dt.append(data)
                                            except absensi_db.DoesNotExist:
                                                ab.kembali = jam_absen.time()
                                                ab.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 11,
                                                    "mesin": a["mesin"],
                                                    "ket": "Kembali Malam"
                                                }
                                                dt.append(data)
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.kembali is not None:
                                                if ab2.kembali.hour < 9:
                                                    ab2.kembali = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.kembali_b = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab2.pulang is not None:
                                                if ab2.pulang.hour < 9:
                                                    ab2.kembali = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.kembali_b = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                if ab2.masuk_b is not None:
                                                    ab2.kembali_b = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.kembali = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 11,
                                                        "mesin": a["mesin"],
                                                        "ket": "Kembali Malam"
                                                    }
                                                    dt.append(data)
                                        except absensi_db.DoesNotExist:
                                            ab.kembali = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 11,
                                                "mesin": a["mesin"],
                                                "ket": "Kembali Malam"
                                            }
                                            dt.append(data)
                                else:
                                    pass
# ++++++++++++++++++++++++++++++++++++++++  PULANG  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 1 and int(jam_absen.hour) > 9:
                            if ab.pulang is None: 
                                if ab.istirahat_b is not None or ab.kembali_b is not None:
                                    ab.pulang_b = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 11,
                                        "mesin": a["mesin"],
                                        "ket": "Pulang B"
                                    }
                                    dt.append(data)
                                else:
                                    ab.pulang = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 1,
                                        "mesin": a["mesin"],
                                        "ket": "Pulang"
                                    }
                                    dt.append(data)
                            else:
                                d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(r.date(),ab.pulang)
                                if d.total_seconds() / 3600 > 3:
                                    ab.pulang_b = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 11,
                                        "mesin": a["mesin"],
                                        "ket": "Pulang B"
                                    }
                                    dt.append(data)
                                else:
                                    ab.pulang = jam_absen.time()
                                    ab.save()
                                    data = {
                                        "userid": a["userid"],
                                        "jam_absen": jam_absen,
                                        "punch": 1,
                                        "mesin": a["mesin"],
                                        "ket": "Pulang"
                                    }
                                    dt.append(data)
# ++++++++++++++++++++++++++++++++++++++++  PULANG MALAM  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                        elif a["punch"] == 1 and int(jam_absen.hour) < 9:
                            if pg is not None:
                                if pg["status_id"] == 3:
                                    if ab.masuk is not None:
                                        if int(ab.masuk.hour) > 18:
                                            ab.pulang = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 7,
                                                "mesin": a["mesin"],
                                                "ket": "Pulang Malam"
                                            }
                                            dt.append(data)
                                        else:
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 7,
                                                "mesin": a["mesin"],
                                                "ket": "Pulang Malam"
                                            }
                                            dt.append(data)
                                    else:
                                        try:
                                            ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                            if ab2.pulang is not None:
                                                d = datetime.combine(r.date(),jam_absen.time()) - datetime.combine(ab2.tgl_absen,ab2.pulang)
                                                if d.total_seconds() / 3600 > 5:
                                                    ab.pulang = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 7,
                                                        "mesin": a["mesin"],
                                                        "ket": "Pulang Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.pulang = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 7,
                                                        "mesin": a["mesin"],
                                                        "ket": "Pulang Malam"
                                                    }
                                                    dt.append(data)
                                            elif ab.istirahat is not None or ab.kembali is not None or ab.masuk is not None:
                                                ab.pulang = jam_absen.time()
                                                ab.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                            elif ab2.masuk is not None:
                                                if int(ab2.masuk.hour) < 18:
                                                    ab.pulang = jam_absen.time()
                                                    ab.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen,
                                                        "punch": 7,
                                                        "mesin": a["mesin"],
                                                        "ket": "Pulang Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    ab2.pulang = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 7,
                                                        "mesin": a["mesin"],
                                                        "ket": "Pulang Malam"
                                                    }
                                                    dt.append(data)
                                            else:
                                                ab2.pulang = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        except absensi_db.DoesNotExist:
                                            ab.pulang = jam_absen.time()
                                            ab.save()
                                            data = {
                                                "userid": a["userid"],
                                                "jam_absen": jam_absen,
                                                "punch": 7,
                                                "mesin": a["mesin"],
                                                "ket": "Pulang Malam"
                                            }
                                            dt.append(data)
                                else:
                                    try:
                                        ab2 = absensi_db.objects.get(tgl_absen=tmin.date(),pegawai__userid=a["userid"])
                                        if ab2.pulang is not None:
                                            if ab2.pulang.hour < 9:
                                                ab2.pulang = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.pulang_b = jam_absen.time()
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.masuk is not None:
                                            if ab2.masuk.hour > 18:
                                                ab2.pulang = jam_absen
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.istirahat is not None:
                                            if ab2.istirahat.hour < 9:
                                                ab2.pulang = jam_absen
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.kembali is not None:
                                            if ab2.kembali.hour < 9:
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen,
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        elif ab2.pulang is not None:
                                            if ab2.pulang.hour < 9:
                                                ab2.pulang = jam_absen
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                            else:
                                                ab2.pulang_b = jam_absen
                                                ab2.save()
                                                data = {
                                                    "userid": a["userid"],
                                                    "jam_absen": jam_absen - timedelta(days=1),
                                                    "punch": 7,
                                                    "mesin": a["mesin"],
                                                    "ket": "Pulang Malam"
                                                }
                                                dt.append(data)
                                        else:
                                            if ab2.masuk_b is not None:
                                                if int(ab2.masuk_b.hour) > 18:
                                                    ab2.pulang_b = jam_absen.time()
                                                    ab2.save()
                                                    data = {
                                                        "userid": a["userid"],
                                                        "jam_absen": jam_absen - timedelta(days=1),
                                                        "punch": 7,
                                                        "mesin": a["mesin"],
                                                        "ket": "Pulang Malam"
                                                    }
                                                    dt.append(data)
                                                else:
                                                    pass
                                            else:
                                                ab2.pulang = jam_absen.time()
                                                ab2.save()
                                    except absensi_db.DoesNotExist:
                                        ab.pulang = jam_absen.time()
                                        ab.save()
                                        data = {
                                            "userid": a["userid"],
                                            "jam_absen": jam_absen,
                                            "punch": 7,
                                            "mesin": a["mesin"],
                                            "ket": "Pulang Malam"
                                        }
                                        dt.append(data)


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
                    if p['hari_off'] == nh:
                        # jika dia bisa mendapatkan opg 
                        if p['status_id'] in lsopg:
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
                    ab.libur_nasional = None
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
    return redirect ('absensi',sid=int(sid))   

@login_required
def detail_absensi(r,userid,tgl,sid):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses

        dsid = dakses.sid_id  

        pgw = pegawai_db.objects.get(userid=userid)

        # get absensi
        ab = absensi_db.objects.get(pegawai__userid=userid,tgl_absen=tgl)

        # get all jam kerja 
        jk = jamkerja_db.objects.filter(kk_id=pgw.kelompok_kerja.pk)

        # dt_raw = sorted(draw,key=lambda i: i["jam_absen"])
        status = status_pegawai_db.objects.all().order_by('id')
        

        # get kk 
        kk = jamkerja_db.objects.filter(kk_id=pgw.kelompok_kerja.pk)
        dt_kk = []
        for k in kk:
            obj = {
                "kk":k.kk.kelompok,
                "jam_masuk":k.jam_masuk.strftime('%H:%M:%S'),
                "jam_pulang": k.jam_pulang.strftime('%H:%M:%S'),
                "jam_istirahat": k.jam_istirahat.strftime('%H:%M:%S'),
                "jam_kembali_istirahat": k.jam_kembali_istirahat.strftime('%H:%M:%S'),
                "jam_istirahat2":k.jam_istirahat2.strftime('%H:%M:%S'),
                "jam_kembali_istirahat2":k.jam_kembali_istirahat2.strftime('%H:%M:%S'),
                "hari":k.hari
            }
            selisih = datetime.combine(date.today(),k.jam_kembali_istirahat) - datetime.combine(date.today(),k.jam_istirahat)
            obj["lama_istirahat"] = selisih.total_seconds() / 3600
            dt_kk.append(obj)

        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
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
    raw = data_trans_db.objects.filter(userid=userid,jam_absen__date=tgl.date()).order_by("jam_absen")
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
def hapus_jam(r):
    if r.headers['x-requested-with'] == 'XMLHttpRequest':
        id = r.POST.get('id')
        if id is not None:
            data_trans_db.objects.get(pk=int(id)).delete()
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
        ).save()
        return JsonResponse({"status":"ok"})
    
@login_required
def ubah_absen(r):
    id = r.POST.get('id')
    absen = r.POST.get('absen')
    absen = absen.split("|")

    if data_trans_db.objects.filter(pk=int(id)).exists():
        ab = data_trans_db.objects.get(pk=int(id))
        ab.punch = absen[0]
        ab.keterangan = absen[1]
        ab.save()
    return JsonResponse({"ok":"ok"})

@login_required
def pu(r,tgl,userid,sid):
    dt = data_trans_db.objects.filter(jam_absen__date=tgl,userid=userid).order_by('jam_absen')
    abs = absensi_db.objects.get(tgl_absen=tgl,pegawai__userid=userid)
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
    abs.save()
    return redirect("dabsen",userid=userid,tgl=tgl,sid=sid)

@login_required
def edit_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")
    ket = r.POST.get("ket")
    id = r.POST.get("id")
    sid = r.POST.get("sid")

    if jenis_ijin_db.objects.filter(pk=int(jenis_ijin)).exists():
        if absensi_db.objects.filter(pk=int(id)).exists():
            ji = jenis_ijin_db.objects.get(pk=int(jenis_ijin))
            ab = absensi_db.objects.get(pk=int(id))
            ab.keterangan_ijin = f'{ji.jenis_ijin}-({ket})'
            ab.save()
            ijin_db(
                pegawai_id = ab.pegawai_id,
                tgl_ijin = ab.tgl_absen,
                ijin_id = ji.pk,
                keterangan = ket,
                add_by = 'Program'
            ).save()
    return JsonResponse({"ok":"ok"})

@login_required
def edit_jamkerja(r,userid,tgl,sid):
    masuk = r.POST.get("jam_masuk")
    keluar = r.POST.get("jam_keluar")
    istirahat = r.POST.get("jam_istirahat")
    lama_ist = r.POST.get("lama_istirahat")
    id = r.POST.get("id")
    
    if absensi_db.objects.filter(pk=int(id)).exists():
        ab = absensi_db.objects.get(pk=int(id))
        ab.jam_masuk = masuk
        ab.jam_pulang = keluar
        ab.jam_istirahat = istirahat
        ab.lama_istirahat = lama_ist
        ab.save()
    return redirect("dabsen",userid=userid,tgl=tgl,sid=sid)


def absensi_id(r):
    idp = r.POST.get('id')
    tgl = r.POST.get('tgl')
    tgl = datetime.strptime(tgl,"%d-%m-%Y")
    tgl = tgl.strftime("%Y-%m-%d")
    if absensi_db.objects.filter(pegawai_id=idp,tgl_absen=tgl).exists():
        ab = absensi_db.objects.get(pegawai_id=idp,tgl_absen=tgl)
        data = {
            "lama_istirahat":ab.lama_istirahat,
            "lama_istirahat2":ab.lama_istirahat2,
        }
        return JsonResponse({"status":"ok","data":data})
    else:
        return JsonResponse({"status":"null","data":{}})