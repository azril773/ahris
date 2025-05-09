from hrd_app.controllers.lib import *


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Lembur
@authorization(["*"])
def lembur(r, sid):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
        dari = datetime.strptime(pa[0].date().strftime("%d-%m-%Y"),"%d-%m-%Y").date()
        sampai = datetime.strptime(pa[1].date().strftime("%d-%m-%Y"),"%d-%m-%Y").date()
        prd = pa[2]
        thn = pa[3]
        bln = nama_bulan(int(prd))
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        statuspgw = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id = sid).last()
        ids = 0            
        if statuspgw is not None:
            ids = statuspgw.pk
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for pp in list_pegawai_lembur_db.objects.select_related("pegawai__divisi","pegawai__status").using(r.session["ccabang"]).filter(pegawai__divisi_id__in=aksesdivisi).distinct("pegawai__status_id"):
            statusid.append(pp.pegawai.status_id)
            # print(p)
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")
        pegawai = []
        for p in list_pegawai_lembur_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").filter(pegawai__divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.pegawai.id,
                    'nama':p.pegawai.nama,
                    'nik':p.pegawai.nik,
                    'userid':p.pegawai.userid
                }    
                pegawai.append(data)
            else:
                if p.pegawai.status_id == sid:     
                    data = {
                        'idp':p.pegawai.id,
                        'nama':p.pegawai.nama,
                        'nik':p.pegawai.nik,
                        'userid':p.pegawai.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
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
        
        return render(r,'hrd_app/lembur/lembur/[sid]/lembur.html', data)
        
    else:    
        messages.error(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def lembur_belum_proses(r, sid):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
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
        statuspgw = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id = sid).last()
        ids = 0            
        if statuspgw is not None:
            ids = statuspgw.pk
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for pp in list_pegawai_lembur_db.objects.select_related("pegawai__divisi","pegawai__status").using(r.session["ccabang"]).filter(pegawai__divisi_id__in=aksesdivisi).distinct("pegawai__status_id"):
            statusid.append(pp.pegawai.status_id)
            # print(p)
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")
        sid_lembur = 0
        pegawai = []
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1):
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
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
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
            'prd':int(prd),
            'thn':int(thn),
            'nama_bulan':bln,
            'modul_aktif' : 'Lembur'
        }
        
        return render(r,'hrd_app/lembur/belum_proses/[sid]/belum_proses.html', data)
        
    else:    
        messages.error(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def cari_lembur(r):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        periode = r.POST.get('periode')
        tahun = r.POST.get('tahun')
        sid = r.POST.get('sid')
        bln = nama_bulan(int(periode))
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        lstatus = []
        sid_lembur = 0
        pegawai = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").filter(aktif=1,divisi_id__in=aksesdivisi):
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
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
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
        
        return render(r,'hrd_app/lembur/cari_lembur.html', data)
        
    else:    
        messages.error(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def tambah_lembur(r):
    try:
        nama_user = r.session["user"]["nama"]
        
        sid = r.POST.get('sid')
        dtgl = r.POST.get('tgl')
        idp = int(r.POST.get('pegawai'))
        awal = float(r.POST.get('awal'))
        akhir = float(r.POST.get('akhir'))
        ist_1 = float(r.POST.get('ist_1'))
        ist_2 = float(r.POST.get('ist_2'))
    
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
        with transaction.atomic(using=r.session["ccabang"]):
            try:
                aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
                if lembur_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), tgl_lembur=tgl).exists():
                    raise Exception('Lembur sudah.') 
                else:
                    # jika absensi ada
                    if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(tgl_absen=tgl, pegawai_id=int(idp),pegawai__divisi_id__in=aksesdivisi).exists():
                        ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(tgl_absen=tgl, pegawai_id=int(idp),pegawai__divisi_id__in=aksesdivisi)            
                        
                        # Dengan istirahat (di jadwal kerja)
                        if ab.lama_istirahat != 0 or ab.lama_istirahat is not None:
                            if ab.masuk is not None and ab.pulang is not None or ab.masuk_b is not None and ab.pulang_b is not None:
                                
                                jadwal_masuk = datetime.combine(ab.tgl_absen, ab.jam_masuk) 
                                jadwal_pulang = datetime.combine(ab.tgl_absen, ab.jam_pulang)
                                if ab.masuk is not None and ab.pulang is not None:
                                    absen_masuk = datetime.combine(ab.tgl_absen, ab.masuk)
                                    absen_pulang = datetime.combine(ab.tgl_absen, ab.pulang)
                                elif ab.masuk_b is not None and ab.pulang_b is not None:
                                    absen_masuk = datetime.combine(ab.tgl_absen, ab.masuk_b)
                                    absen_pulang = datetime.combine(ab.tgl_absen, ab.pulang_b)
                                bm = jadwal_masuk + timedelta(minutes=5)
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

                                    mulai_plg = batas_pulang - timedelta(minutes=5)  
                                    tutuptoko = tutup_toko_db.objects.using(r.session["ccabang"]).all().last()
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
                                    if tutuptoko.jam_tutup == batas_pulang.time() and absen_pulang < (datetime.combine(ab.tgl_absen,batas_pulang) - timedelta(minutes=3)).time():
                                        pemotong_plg += 0.5
                                    # -------------------------------------------------
                                    # pemotong jam istirahat
                                    
                                    if ab.istirahat is not None and ab.kembali is not None:
                                        
                                        absen_ist = datetime.combine(ab.tgl_absen, ab.istirahat)
                                        absen_kmb = datetime.combine(ab.tgl_absen, ab.kembali)
                                        
                                        if ab.istirahat2 is None and ab.kembali2 is None:
                                            if ab.kembali < ab.istirahat:
                                                raise Exception('Jam istirahat lebih besar dari jam kembali istirahat.')
                                            else:                                    
                                                # -------------------------------------------------
                                                # istirahat 1
                                                if ab.lama_istirahat is not None:
                                                    if ist_1 > ab.lama_istirahat:
                                                        lama_ist = (ab.lama_istirahat * 60) + 5
                                                        decimal_ist = ab.lama_istirahat
                                                    else:
                                                        if ist_1 == 0:
                                                            lama_ist = (ab.lama_istirahat * 60) + 5
                                                            decimal_ist = ab.lama_istirahat
                                                        else:
                                                            lama_ist = (ist_1 * 60) + 5
                                                            decimal_ist = ist_1
                                                            
                                                lama_ist = round(lama_ist)
                                                a_ist = absen_ist + timedelta(minutes=lama_ist)
                                                b_ist.append(a_ist)
                                                for x in range(int(looping) - 1):
                                                    a2_ist = b_ist[x] + timedelta(minutes=30)
                                                    b_ist.append(a2_ist)
                                                # if absen_kmb <= a_ist:
                                                #     selisihkmb = (a_ist - timedelta(minutes=5)) - absen_kmb
                                                #     tist = selisihkmb.total_seconds() / 3600
                                                #     tist = round(abs(float(decimal_ist) - tist),2)
                                                #     decimal_part = abs(int(tist) - tist)
                                                #     if decimal_part <= 0.5:
                                                #         tist = int(tist) + 0.5
                                                #     else:
                                                #         tist = math.ceil(tist)    

                            
                                                #     pemotong_ist = -abs(float(decimal_ist) - tist)
                                                #     pemotong_ist2 = 0
                                                #     s_ist.append(pemotong_ist)
                                                # else:
                                                if a_ist >=  absen_kmb:
                                                    pemotong_ist = 0
                                                    pemotong_ist2 = 0
                                                else:
                                                    for b in b_ist:                             
                                                        if absen_kmb > b:
                                                            pemotong_ist = (b_ist.index(b) + 1) * 0.5
                                                            pemotong_ist2 = 0 
                                                        else:
                                                            pass                                      
                                        else:
                                            # -------------------------------------------------
                                            # istirahat 1
                                            if ab.lama_istirahat is not None:
                                                if ist_1 > ab.lama_istirahat:
                                                    lama_ist = (ab.lama_istirahat * 60) + 5
                                                    decimal_ist = ab.lama_istirahat
                                                else:
                                                    if ist_1 == 0:
                                                        lama_ist = (ab.lama_istirahat * 60) + 5
                                                        decimal_ist = ab.lama_istirahat
                                                    else:
                                                        lama_ist = (ist_1 * 60) + 5
                                                        decimal_ist = ist_1                                 
                                            lama_ist = round(lama_ist)
                                            a_ist = absen_ist + timedelta(minutes=lama_ist)  
                                            b_ist.append(a_ist)     
                                            
                                            for x in range(int(looping) - 1):
                                                a2_ist = b_ist[x] + timedelta(minutes=30)
                                                b_ist.append(a2_ist)
                                            if a_ist > absen_kmb:
                                                    # selisihkmb = (a_ist - timedelta(minutes=5)) - absen_kmb


                                                    # tist = selisihkmb.total_seconds() / 3600
                                                    # tist = round(abs(float(decimal_ist) - tist),2)


                                                    # decimal_part = abs(int(tist) - tist)
                                                    # if decimal_part <= 0.5:
                                                    #     tist = int(tist) + 0.5
                                                    # else:
                                                    #     tist = math.ceil(tist)    
                                                    pemotong_ist = 0
                                                    pemotong_ist2 = 0
                                                    # s_ist.append(pemotong_ist)
                                            else:
                                                for b in b_ist:                             
                                                    if absen_kmb > b:
                                                        pemotong_ist = (b_ist.index(b) + 1) * 0.5  
                                                    else:
                                                        pass 
                                            
                                            if ab.kembali2 < ab.istirahat2:
                                                raise Exception('Jam istirahat 2 lebih besar dari jam kembali istirahat 2.')
                                            else:
                                                # -------------------------------------------------
                                                # istirahat 2
                                                
                                                absen_ist2 = datetime.combine(ab.tgl_absen, ab.istirahat2)
                                                absen_kmb2 = datetime.combine(ab.tgl_absen, ab.kembali2)

                                                if ab.lama_istirahat2 is not None:
                                                    if ist_2 > ab.lama_istirahat2:
                                                        lama_ist2 = (ab.lama_istirahat2 * 60) + 5
                                                        decimal_ist2 = ab.lama_istirahat2
                                                    else:
                                                        if ist_2 == 0:
                                                            lama_ist2 = (ab.lama_istirahat2 * 60) + 5
                                                            decimal_ist2 = ab.lama_istirahat2
                                                        else:
                                                            lama_ist2 = (ist_2 * 60) + 5
                                                            decimal_ist2 = ist_2
                                                lama_ist2 = round(lama_ist2)
                                                a_ist2 = absen_ist2 + timedelta(minutes=lama_ist2)  
                                                b_ist2.append(a_ist2)     
                                                
                                                for x in range(int(looping) - 1):
                                                    a2_ist2 = b_ist2[x] + timedelta(minutes=30)
                                                    b_ist2.append(a2_ist2)
                                                if absen_kmb2 <= a_ist2:
                                                    # selisihkmb = (a_ist2 - timedelta(minutes=5)) - absen_kmb2
                                                    # tist = selisihkmb.total_seconds() / 3600
                                                    # tist = round(abs(float(decimal_ist2) - tist),2)
                                                    # decimal_part = abs(int(tist) - tist)
                                                    # if decimal_part <= 0.5:
                                                    #     tist = int(tist) + 0.5
                                                    # else:
                                                    #     tist = math.ceil(tist)    

                            
                                                    # pemotong_ist2 = -abs(float(decimal_ist2) - tist)
                                                    pemotong_ist = 0
                                                    pemotong_ist2 = 0
                                                else:
                                                    for b in b_ist2:                             
                                                        if absen_kmb2 > b:
                                                            pemotong_ist2 = (b_ist2.index(b) + 1) * 0.5  
                                                        else:
                                                            pass                                      
                                                
                                    else:                   
                                        pemotong_ist = -ab.lama_istirahat
                                        pemotong_ist2 = 0
                                    # pemotong_ist = -1
                                    # pemotong_ist2 = 0
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
                                    print(awal,akhir,pemotong_msk,pemotong_plg,pi)
                                    if awal > 0 and akhir > 0:
                                        lembur = Decimal((awal + akhir)) - (pemotong_msk + pi + pemotong_plg)
                                    elif awal > 0 and akhir == 0:     
                                        lembur = (awal) - (pemotong_msk + pi + pemotong_plg)
                                    elif awal == 0 and akhir > 0:
                                        lembur = (akhir) - (pemotong_msk + pi + pemotong_plg)
                                    print(lembur)
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
                                    tambah_lembur.save(using=r.session["ccabang"])  
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
                                    tambah_lembur.save(using=r.session["ccabang"])   
                                    return redirect('lembur_bproses', int(sid))          
                                
                            else:
                                raise Exception('Absen Tidak Lengkap.')
                            
                
                        # Tanpa istirahat (di jadwal kerja)
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
                                    
                                # pengelolaan lembur
                                if lebih == 0:
                                    if ab.pulang < ab.masuk:
                                        raise Exception('Jam Masuk lebih besar dari Jam Pulang.') 
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
                                        if ab.istirahat is not None and ab.kembali is not None:
                                            selisih = datetime.combine(ab.tgl_absen, ab.kembali) - datetime.combine(ab.tgl_absen, ab.istirahat)
                                            selisih = selisih.total_seconds() / 3600
                                            pemotong_ist = selisih
                                        else:
                                            pemotong_ist = 0
                                        
                                        if ab.istirahat2 is not None and ab.kembali2 is not None:
                                            selisih2 = datetime.combine(ab.tgl_absen, ab.kembali2) - datetime.combine(ab.tgl_absen, ab.istirahat2)
                                            selisih2 = selisih2.total_seconds() / 3600
                                            pemotong_ist2 = selisih2
                                        else:
                                            pemotong_ist2 = 0
                                        
                                        # -------------------------------------------------
                                        # pemotong jam pulang                                
                                        
                                        if akhir == 0:                                       
                                            batas_pulang = jadwal_pulang
                                        else:  
                                            batas_pulang = jadwal_pulang + timedelta(hours=akhir)                                      
                                            
                                        mulai_plg = batas_pulang - timedelta(minutes=5)  
                                        tutuptoko = tutup_toko_db.objects.using(r.session["ccabang"]).all().last()
                                                                        
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
                                        if absen_pulang >= (datetime.combine(ab.tgl_absen,tutuptoko.jam_tutup) - timedelta(minutes=30)) and absen_pulang < (datetime.combine(ab.tgl_absen,tutuptoko.jam_tutup) - timedelta(minutes=3)):
                                            pemotong_plg += 0.5                                
                                        
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
                                        tambah_lembur.save(using=r.session["ccabang"])
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
                                    tambah_lembur.save(using=r.session["ccabang"])     
                                    return redirect('lembur_bproses', int(sid))             
                                            
                            else:
                                raise Exception('Absen Tidak Lengkap.')
                    
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
                        tambah_lembur.save(using=r.session["ccabang"])
                        return redirect('lembur_bproses', int(sid))

                # insert or update rekap lembur
                # -------------------------------------------------------------
                # hitung total lembur'
                tl = lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
                if tl['total'] is None:
                    tlembur = 0
                else:
                    tlembur = tl['total'] 
                
                # hitung total kompen
                kp = kompen_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
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
                if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), periode=prds, tahun=thns).exists():
                    rkps = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), periode=prds, tahun=thns)
                    sisa_lembur_sbl = rkps.sisa_lembur
                else:
                    sisa_lembur_sbl = 0     
                    
                # input or update rekap lembur  
                if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), periode=prd, tahun=thn).exists():
                    rk = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), periode=prd, tahun=thn)
                    
                    rk.total_lembur = float(sisa_lembur_sbl + tlembur)
                    rk.total_kompen = float(tkompen)
                    rk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(rk.lembur_jam_bayar)
                    rk.edit_by = nama_user          
                    rk.save(using=r.session["ccabang"])
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
                    tambah_rekap.save(using=r.session["ccabang"])
                
                return redirect('lembur', int(sid))
            except Exception as e:
                transaction.set_rollback(True,using=r.session["ccabang"])
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
                raise Exception(msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
        messages.error(r,msg)
        return redirect("lembur",sid=sid)

@authorization(["*"])
def proses_ulang_lembur(r, idl):
    try:
        nama_user = r.session["user"]["nama"]
        
        lb = lembur_db.objects.using(r.session["ccabang"]).filter(id=int(idl)).last()
        if not lb:
            raise Exception("Lembur tidak ada")
        
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
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        # jika absensi ada
        with transaction.atomic(using=r.session['ccabang']):
            try:
                if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(tgl_absen=tgl, pegawai_id=int(idp),pegawai__divisi_id__in=aksesdivisi).exists():
                    ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(tgl_absen=tgl, pegawai_id=int(idp),pegawai__divisi_id__in=aksesdivisi)            
                    
                    # Tanpa istirahat (di jadwal kerja)
                    if (ab.lama_istirahat == 0 and ab.lama_istirahat is not None) or ab.lama_istirahat is None:
                        if ab.masuk is not None and ab.pulang is not None:
                            
                            jadwal_masuk = datetime.combine(ab.tgl_absen, ab.jam_masuk)
                            jadwal_pulang = datetime.combine(ab.tgl_absen, ab.jam_pulang)
                                
                            absen_masuk = datetime.combine(ab.tgl_absen, ab.masuk)
                            absen_pulang = datetime.combine(ab.tgl_absen, ab.pulang)
                            
                            bm = jadwal_masuk + timedelta(minutes=4)
                            batas_masuk = datetime.strptime(str(bm), "%Y-%m-%d %H:%M:%S")            
                                                    
                            # pengelolaan lembur
                            if ab.pulang < ab.masuk:
                                raise Exception('Jam Masuk lebih besar dari Jam Pulang.') 
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
                                    
                                mulai_plg = batas_pulang - timedelta(minutes=5) 
                                tutuptoko = tutup_toko_db.objects.using(r.session["ccabang"]).all().last() 
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
                                if absen_pulang >= (datetime.combine(ab.tgl_absen,tutuptoko.jam_tutup) - timedelta(minutes=30)) and absen_pulang < (datetime.combine(ab.tgl_absen,tutuptoko.jam_tutup) - timedelta(minutes=3)):
                                    pemotong_plg += 0.5                        
                                
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
                                lb.save(using=r.session["ccabang"])                        
                                            
                        else:
                            raise Exception('Absen Tidak Lengkap.')
                
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
                                raise Exception('Jam Masuk lebih besar dari Jam Pulang.')
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
                                    
                                mulai_plg = batas_pulang - timedelta(minutes=5)  
                                tutuptoko = tutup_toko_db.objects.using(r.session["ccabang"]).all().last()
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
                                if absen_pulang > (datetime.combine(ab.tgl_absen,tutuptoko.jam_tutup) - timedelta(minutes=30)) and absen_pulang < (datetime.combine(ab.tgl_absen,tutuptoko.jam_tutup) - timedelta(minutes=3)):
                                    pemotong_plg += 0.5       
                                # -------------------------------------------------
                                # pemotong jam istirahat
                                
                                if ab.istirahat is not None and ab.kembali is not None:
                                    
                                    absen_ist = datetime.combine(ab.tgl_absen, ab.istirahat)
                                    absen_kmb = datetime.combine(ab.tgl_absen, ab.kembali)
                                    
                                    if ab.istirahat2 is None and ab.kembali2 is None:
                                        if ab.kembali < ab.istirahat:
                                            raise Exception('Jam istirahat lebih besar dari jam kembali istirahat.')
                                        else:                                    
                                            # -------------------------------------------------
                                            # istirahat 1
                                            
                                            if ab.lama_istirahat is not None:
                                                if ist_1 > ab.lama_istirahat:
                                                    lama_ist = (ab.lama_istirahat * 60) + 5
                                                    decimal_ist = ab.lama_istirahat
                                                else:
                                                    if ist_1 == 0:
                                                        lama_ist = (ab.lama_istirahat * 60) + 5
                                                        decimal_ist = ab.lama_istirahat
                                                    else:
                                                        lama_ist = (ist_1 * 60) + 5
                                                        decimal_ist = ist_1
                                                        
                                            lama_ist = round(lama_ist)
                                            a_ist = absen_ist + timedelta(minutes=lama_ist)
                                            b_ist.append(a_ist)
                                            for x in range(int(looping) - 1):
                                                a2_ist = b_ist[x] + timedelta(minutes=30)
                                                b_ist.append(a2_ist)
                                            if absen_kmb <= a_ist:
                                                # selisihkmb = (a_ist - timedelta(minutes=5)) - absen_kmb
                                                # tist = selisihkmb.total_seconds() / 3600
                                                # tist = round(abs(float(decimal_ist) - tist),2)
                                                # decimal_part = abs(int(tist) - tist)
                                                # if decimal_part <= 0.5:
                                                #     tist = int(tist) + 0.5
                                                # else:
                                                #     tist = math.ceil(tist)    
                            
                                                # pemotong_ist = -abs(float(decimal_ist) - tist)
                                                # pemotong_ist2 = 0
                                                # s_ist.append(pemotong_ist)
                                                pemotong_ist = 0
                                                pemotong_ist2 = 0
                                            else:
                                                for b in b_ist:                             
                                                    if absen_kmb > b:
                                                        pemotong_ist = (b_ist.index(b) + 1) * 0.5  
                                                        pemotong_ist2 = 0 
                                                    else:
                                                        pass                                      
                                            
                                    else:
                                        # -------------------------------------------------
                                        # istirahat 1
                                        
                                        if ab.lama_istirahat is not None:
                                            if ist_1 > ab.lama_istirahat:
                                                lama_ist = (ab.lama_istirahat * 60) + 5
                                                decimal_ist = ab.lama_istirahat
                                            else:
                                                if ist_1 == 0:
                                                    lama_ist = (ab.lama_istirahat * 60) + 5
                                                    decimal_ist = ab.lama_istirahat
                                                else:
                                                    lama_ist = (ist_1 * 60) + 5
                                                    decimal_ist = ist_1
                                                    
                                        lama_ist = round(lama_ist)
                                        a_ist = absen_ist + timedelta(minutes=lama_ist)
                                        b_ist.append(a_ist)
                                        for x in range(int(looping) - 1):
                                            a2_ist = b_ist[x] + timedelta(minutes=30)
                                            b_ist.append(a2_ist)
                                        if absen_kmb <= a_ist:
                                            # selisihkmb = (a_ist - timedelta(minutes=5)) - absen_kmb
                                            # tist = selisihkmb.total_seconds() / 3600
                                            # tist = round(abs(float(decimal_ist) - tist),2)
                                            # decimal_part = abs(int(tist) - tist)
                                            # if decimal_part <= 0.5:
                                            #     tist = int(tist) + 0.5
                                            # else:
                                            #     tist = math.ceil(tist)   
                        
                                            # pemotong_ist = -abs(float(decimal_ist) - tist)
                                            # pemotong_ist2 = 0
                                            pemotong_ist = 0
                                            pemotong_ist2 = 0
                                        else:
                                            for b in b_ist:                             
                                                if absen_kmb > b:
                                                    pemotong_ist = (b_ist.index(b) + 1) * 0.5  
                                                    pemotong_ist2 = 0 
                                                else:
                                                    pass 
                                        
                                        if ab.kembali2 < ab.istirahat2:
                                            raise Exception('Jam istirahat 2 lebih besar dari jam kembali istirahat 2.')
                                        else:
                                            # -------------------------------------------------
                                            # istirahat 2
                                            
                                            absen_ist2 = datetime.combine(ab.tgl_absen, ab.istirahat2)
                                            absen_kmb2 = datetime.combine(ab.tgl_absen, ab.kembali2)
                                            
                                            if ab.lama_istirahat2 is not None:
                                                if ist_2 > ab.lama_istirahat2:
                                                    lama_ist2 = (ab.lama_istirahat2 * 60) + 5
                                                    decimal_ist2 = ab.lama_istirahat2
                                                else:
                                                    if ist_2 == 0:
                                                        lama_ist2 = (ab.lama_istirahat2 * 60) + 5
                                                        decimal_ist2 = ab.lama_istirahat2
                                                    else:
                                                        lama_ist2 = (ist_2 * 60) + 5
                                                        decimal_ist2 = ist_2
                                            lama_ist2 = round(lama_ist2)
                                            a_ist2 = absen_ist2 + timedelta(minutes=lama_ist2)  
                                            b_ist2.append(a_ist2)     
                                            
                                            for x in range(int(looping) - 1):
                                                a2_ist2 = b_ist2[x] + timedelta(minutes=30)
                                                b_ist2.append(a2_ist2)
                                            if absen_kmb2 <= a_ist2:
                                                # selisihkmb = (a_ist2 - timedelta(minutes=5)) - absen_kmb2
                                                # tist = selisihkmb.total_seconds() / 3600
                                                # tist = round(abs(float(decimal_ist2) - tist),2)
                                                # decimal_part = abs(int(tist) - tist)
                                                # if decimal_part <= 0.5:
                                                #     tist = int(tist) + 0.5
                                                # else:
                                                #     tist = math.ceil(tist)    
                            
                                                # pemotong_ist2 = -abs(float(decimal_ist2) - tist)
                                                # pemotong_ist = s_ist[0]
                                                pemotong_ist = 0
                                                pemotong_ist2 = 0
                                            else:
                                                for b in b_ist2:                             
                                                    if absen_kmb2 > b:
                                                        pemotong_ist2 = (b_ist2.index(b) + 1) * 0.5  
                                                    else:
                                                        pass                                      
                                        
                                else:                                
                                    pemotong_ist = Decimal(-ab.lama_istirahat)
                                    pemotong_ist2 = Decimal(-ab.lama_istirahat2)

                                # additional perhitungan istirahat
                                if ist_1 + ist_2 > 1:
                                    selisih_pi = (ist_1+ist_2) - 1
                                    pi = (pemotong_ist + pemotong_ist2) + selisih_pi
                                else:
                                    pi = pemotong_ist + pemotong_ist2    
                                
                                # perhitungan lembur
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
                                    
                                lb.status = 1
                                lb.proses_lembur = lembur
                                if lb.lebih_nproses > 0:
                                    lb.keterangan = 'Diproses tanpa menambahkan kelebihan jam' 
                                else:
                                    lb.keterangan = ''
                                lb.edit_by = nama_user
                                lb.save(using=r.session["ccabang"])             
                        else:
                            raise Exception('Absen Tidak Lengkap.')
                
                # jika tidak ada absensi
                else:   
                    return redirect('lembur_bproses', int(sid))

                # insert or update rekap lembur
                # -------------------------------------------------------------
                # hitung total lembur
                tl = lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
                if tl['total'] is None:
                    tlembur = 0
                else:
                    tlembur = tl['total']    
                
                # hitung total kompen
                kp = kompen_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
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
                if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), periode=prds, tahun=thns).exists():
                    rkps = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), periode=prds, tahun=thns)
                    sisa_lembur_sbl = rkps.sisa_lembur
                else:
                    sisa_lembur_sbl = 0     
                    
                # input or update rekap lembur  
                if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), periode=prd, tahun=thn).exists():
                    rk = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(pegawai__divisi_id__in=aksesdivisi,pegawai_id=int(idp), periode=prd, tahun=thn)
                    
                    rk.total_lembur = float(sisa_lembur_sbl + tlembur)
                    rk.total_kompen = float(tkompen)
                    rk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(rk.lembur_jam_bayar)
                    rk.edit_by = nama_user          
                    rk.save(using=r.session["ccabang"])
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
                    tambah_rekap.save(using=r.session["ccabang"])
                
                return redirect('lembur', sid=int(sid))
            except Exception as e:
                transaction.set_rollback(True,using=r.session['ccabang'])
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
                raise Exception(msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
        messages.error(r,msg)
        return redirect("lembur",sid=0)


@authorization(["*"])
def batal_lembur(r):
    try:
        nama_user = r.session["user"]["nama"]
        
        idl = r.POST.get('id')
        
        lb = lembur_db.objects.using(r.session["ccabang"]).get(id=int(idl))
        pg = pegawai_db.objects.using(r.session["ccabang"]).get(id=lb.pegawai_id)
        idp = pg.id
        
        ftgl = datetime.strftime(lb.tgl_lembur,'%d-%m-%Y')
    
        pt = periode_tgl(ftgl)
        dr = pt[0]
        sp = pt[1]
        prd = pt[2]
        thn = pt[3]
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        with transaction.atomic(using=r.session["ccabang"]):
            try:
                if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,pegawai_id=idp, periode=prd, tahun=thn).exists():
                    drk = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(pegawai__divisi_id__in=aksesdivisi,pegawai_id=idp, periode=prd, tahun=thn)
                    sisa_lembur_sekarang = drk.sisa_lembur
                    lembur_sekarang = lb.proses_lembur
                
                    if lembur_sekarang > sisa_lembur_sekarang:
                        status = 'batalkan kompen'
                    else:    
                    
                        histori = histori_hapus_db(
                            delete_by = nama_user,
                            delete_item = f"lembur-(a.n {pg.nama}, tgl:{lb.tgl_lembur})"
                        )
                        histori.save(using=r.session["ccabang"])   
                        
                        lb.delete(using=r.session["ccabang"])    
                    
                        # insert or update rekap lembur
                        # -------------------------------------------------------------
                        # hitung total lembur
                        tl = lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
                        if tl['total'] is None:
                            tlembur = 0
                        else:
                            tlembur = tl['total']    
                        
                        # hitung total kompen
                        kp = kompen_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
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
                        if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, periode=prds, tahun=thns).exists():
                            rkps = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=idp, periode=prds, tahun=thns)
                            sisa_lembur_sbl = rkps.sisa_lembur
                        else:
                            sisa_lembur_sbl = 0     
                                            
                        drk.total_lembur = float(sisa_lembur_sbl) + float(tlembur)
                        drk.total_kompen = float(tkompen)
                        drk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(drk.lembur_jam_bayar)
                        drk.edit_by = nama_user
                        drk.save(using=r.session["ccabang"])        
                                
                        status = 'ok'
                else:
                    histori = histori_hapus_db(
                        delete_by = nama_user,
                        delete_item = f"lembur-(a.n {pg.nama}, tgl:{lb.tgl_lembur})"
                    )
                    histori.save(using=r.session["ccabang"])   
                    
                    lb.delete(using=r.session["ccabang"])   
                    
                    status = 'ok' 
                        
                return JsonResponse({"status": status})
            except Exception as e:
                transaction.set_rollback(True,using=r.session['ccabang'])
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
                raise Exception(msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
        return JsonResponse({"status":"error","msg":msg},status=400)


@authorization(["*"])
def bayar_lembur(r):
    try:
        nama_user = r.session["user"]["nama"]
        
        idr = r.POST.get('idr')
        blembur = r.POST.get('blembur')
        
        rk = rekap_lembur_db.objects.using(r.session["ccabang"]).get(id=int(idr))
        pg = pegawai_db.objects.using(r.session["ccabang"]).get(id=rk.pegawai_id)
        idp = pg.id        
        
        drpl = rp_lembur_db.objects.using(r.session["ccabang"]).last()      
        rp_lembur = drpl.rupiah
        
        pa = periode_absen(rk.periode,rk.tahun)
        dr = pa[0].date()
        sp = pa[1].date()
        prd = pa[2]
        thn = pa[3]  
                
        # insert or update rekap lembur
        # -------------------------------------------------------------
        # hitung total lembur
        tl = lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
        if tl['total'] is None:
            tlembur = 0
        else:
            tlembur = tl['total']    
        
        # hitung total kompen
        kp = kompen_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
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
        if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, periode=prds, tahun=thns).exists():
            rkps = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=idp, periode=prds, tahun=thns)
            sisa_lembur_sbl = rkps.sisa_lembur
        else:
            sisa_lembur_sbl = 0        
            
        if float(tkompen) == 0:
            if float(blembur) > float(tlembur):
                raise Exception("Bayar lembur lebih besar dari lembur")
            else:   
                # update rekap lembur            
                rk.total_lembur = float(sisa_lembur_sbl + tlembur)
                rk.total_kompen = float(tkompen)
                rk.lembur_jam_bayar = float(blembur)
                rk.lembur_rupiah_bayar = float(blembur) * rp_lembur
                rk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(blembur)
                rk.edit_by = nama_user          
                rk.save(using=r.session["ccabang"])
                status = 'ok'     
        else:    
            if float(blembur) > float(rk.sisa_lembur):
                raise Exception("Bayar lembur lebih besar dari lembur")
            else:
                # update rekap lembur            
                rk.total_lembur = float(sisa_lembur_sbl + tlembur)
                rk.total_kompen = float(tkompen)
                rk.lembur_jam_bayar = float(blembur)
                rk.lembur_rupiah_bayar = float(blembur) * rp_lembur
                rk.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(blembur)
                rk.edit_by = nama_user 
                rk.save(using=r.session["ccabang"])           
                status = 'ok'
        
        return JsonResponse({"status": status})
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
        return JsonResponse({"status":"error","msg":msg},status=400)


@authorization(["*"])
def rekap_lembur_json(r, sid, prd, thn):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        data = []
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai__divisi_id__in=aksesdivisi,periode=int(prd), tahun=int(thn)).exists():
        
            for r in rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(periode=int(prd), tahun=int(thn), sisa_lembur__gt=0,pegawai__divisi_id__in=aksesdivisi).order_by('pegawai__divisi__divisi','pegawai__nik'):
                
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
        return JsonResponse({"data": data})


@authorization(["*"])
def lembur_belum_proses_json(r, sid):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest": 
        
        data = []
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        
        for l in lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(status=0,pegawai__divisi_id__in=aksesdivisi).order_by('tgl_lembur','pegawai__divisi__divisi','pegawai__nik'):
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


@authorization(["*"])
def lembur_json(r, idp, prd, thn):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest": 
        data = []
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        pa = periode_absen(prd,thn)
        dr = pa[0].date()
        sp = pa[1].date()
        if int(idp) == 0:
            for l in lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(tgl_lembur__range=(dr,sp), status=1,pegawai__divisi_id__in=aksesdivisi).order_by('tgl_lembur'):
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
        else:
            for l in lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(pegawai_id=int(idp), tgl_lembur__range=(dr,sp), status=1,pegawai__divisi_id__in=aksesdivisi).order_by('tgl_lembur'):
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

@authorization(["*"])
def tambah_kompen(r):
    try:
        nama_user = r.session["user"]["nama"]
        
        dtgl = r.POST.get('tgl_kompen')
        idp = r.POST.get('idp')
        jenis = r.POST.get('jkompen')
        kompen = float(r.POST.get('kompen'))
    
        tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()
        ftgl = datetime.strftime(tgl,'%d-%m-%Y')
        
        pt = periode_tgl(ftgl)
        dr = pt[0]
        sp = pt[1]
        prd = pt[2]
        thn = pt[3]   
        # print(prd,thn)
        rkp = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(periode=prd, tahun=thn,pegawai_id=int(idp))
        if not rkp.exists():
            raise Exception(f"Rekap lembur periode {prd} tahun {thn} tidak ada. Ambil kompen sudah melebihi batas tanggal(25) periode absen")
        rkp = rkp[0]
        sisa_lembur = rkp.sisa_lembur
        
        if kompen > sisa_lembur:
            raise Exception("Kompen lebih besar dari sisa lembur")
        else:    
            with transaction.atomic(using=r.session["ccabang"]):
                try:
                # update absensi
                    if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_absen=tgl).exists():
                        ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=int(idp), tgl_absen=tgl)
                        # total jam kerja 
                        if ab.jam_masuk is not None and ab.pulang is not None:
                            if ab.masuk is not None and ab.pulang is not None:
                                
                                jm = datetime.combine(ab.tgl_absen,ab.jam_masuk)
                                jp = datetime.combine(ab.tgl_absen,ab.jam_pulang)
                                
                                njm = jm + timedelta(hours=kompen)
                                njp = jp - timedelta(hours=kompen)
                                
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
                                    raise Exception("Jam masuk lebih besar dari jam pulang")
                                    
                                if jenis == 'awal':
                                    jm_baru = njm.time()
                                    jp_baru = ab.jam_pulang
                                    ket = f'Kompen/PJK-Awal {kompen} Jam'
                                elif jenis == 'akhir':
                                    jm_baru = ab.jam_masuk
                                    jp_baru = njp.time()
                                    ket = f'Kompen/PJK-Akhir {kompen} Jam'
                                else:
                                    if sisa_lembur >= 8:
                                        jm_baru = njm.time()
                                        jp_baru = njp.time()
                                        ket = f'Kompen/PJK 1 Hari'
                                    else:
                                        raise Exception("Sisa lembur harus lebih atau sama dengan 8 jam")
                                ab.jam_masuk = jm_baru
                                ab.jam_pulang = jp_baru
                            else:
                                tjk = 0
                                status ='ok'
                        else:
                            tjk = 0
                            status ='ok'

                    
                        if jenis == 'awal':
                            ket = f'Kompen/PJK-Awal {kompen} Jam'
                        elif jenis == 'akhir':
                            ket = f'Kompen/PJK-Akhir {kompen} Jam'
                        else:
                            ket = f'Kompen/PJK 1 Hari'            
                        ab.keterangan_lain = ket
                        ab.total_jam_kerja = round(tjk,1)
                        ab.edit_by = nama_user
                        ab.save(using=r.session["ccabang"])
                        
                    # insert kompen
                    if kompen_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_kompen = tgl).exists():
                        raise Exception("Kompen sudah ada")
                    else:
                        tkompen = kompen_db(
                            pegawai_id = int(idp),
                            tgl_kompen = tgl,            
                            kompen = kompen,
                            jenis_kompen = jenis,
                            add_by = nama_user,
                            edit_by = nama_user
                        )   
                        tkompen.save(using=r.session["ccabang"]) 
                    
                    # insert or update rekap lembur
                    # -------------------------------------------------------------
                    # hitung total lembur
                    tl = lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
                    if tl['total'] is None:
                        tlembur = 0
                    else:
                        tlembur = tl['total']    
                    
                    # hitung total kompen
                    kp = kompen_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
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
                    if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), periode=prds, tahun=thns).exists():
                        rkps = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=int(idp), periode=prds, tahun=thns)
                        sisa_lembur_sbl = rkps.sisa_lembur
                    else:
                        sisa_lembur_sbl = 0     
                        
                    if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), periode=prd, tahun=thn).exists():     
                        
                        rkp.total_lembur = float(sisa_lembur_sbl + tlembur)
                        rkp.total_kompen = float(tkompen)
                        print(sisa_lembur_sbl,tlembur,tkompen,rkp.lembur_jam_bayar)
                        rkp.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(rkp.lembur_jam_bayar)
                        rkp.edit_by = nama_user          
                        rkp.save(using=r.session["ccabang"])     
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
                        tambah_rekap.save(using=r.session["ccabang"])
                    
                    status = 'ok'
                    return JsonResponse({"status": status})
                except Exception as e:
                    transaction.set_rollback(True,using=r.session["ccabang"])
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
                    raise Exception(msg)
        
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
        return JsonResponse({"status":"error","msg":msg},status=400)


@authorization(["*"])
def batal_kompen(r):
    try:
        nama_user = r.session["user"]["nama"]
        
        idk = r.POST.get('id')
        
        kp = kompen_db.objects.using(r.session["ccabang"]).get(id=int(idk))
        pg = pegawai_db.objects.using(r.session["ccabang"]).get(id=kp.pegawai_id)
        idp = pg.id
        
        ftgl = datetime.strftime(kp.tgl_kompen,'%d-%m-%Y')
    
        pt = periode_tgl(ftgl)
        dr = pt[0]
        sp = pt[1]
        prd = pt[2]
        thn = pt[3]   
        
        ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_absen=kp.tgl_kompen).last()
        if not ab:
            raise Exception("Absensi tidak ada")
            
        with transaction.atomic(using=r.session["ccabang"]):
            try:
                # total jam kerja         
                if ab.jam_masuk is not None and ab.jam_pulang is not None:
                    if ab.masuk is not None and ab.pulang is not None:
                        if ab.pulang > ab.masuk:
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
                            
                            status = 'Jam masuk > Jam Pulang'                
                    else:
                        tjk = 0
                        status = 'ok'
                else:
                    tjk = 0
                    status = 'ok'

                ab.keterangan_lain = None
                ab.total_jam_kerja = round(tjk,1)
                ab.edit_by = nama_user
                ab.save(using=r.session["ccabang"])
                
                histori = histori_hapus_db(
                    delete_by = nama_user,
                    delete_item = f"kompen-(a.n {pg.nama}, tgl:{kp.tgl_kompen})"
                )
                histori.save(using=r.session["ccabang"])   
                
                kp.delete(using=r.session["ccabang"])    

                # insert or update rekap lembur
                # -------------------------------------------------------------
                # hitung total lembur
                tl = lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, tgl_lembur__range=(dr,sp)).aggregate(total=Sum('proses_lembur'))
                if tl['total'] is None:
                    tlembur = 0
                else:
                    tlembur = tl['total']    
                
                # hitung total kompen
                kp = kompen_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, tgl_kompen__range=(dr,sp)).aggregate(total=Sum('kompen')) 
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
                if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, periode=prds, tahun=thns).exists():
                    rkps = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=idp, periode=prds, tahun=thns)
                    sisa_lembur_sbl = rkps.sisa_lembur
                else:
                    sisa_lembur_sbl = 0     
                    
                if rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=idp, periode=prd, tahun=thn).exists():           
                        
                    rkp = rekap_lembur_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=idp, periode=prd, tahun=thn)
                    
                    rkp.total_lembur = float(sisa_lembur_sbl + tlembur)
                    rkp.total_kompen = float(tkompen)
                    rkp.sisa_lembur = float(sisa_lembur_sbl + tlembur) - float(tkompen) - float(rkp.lembur_jam_bayar)
                    rkp.edit_by = nama_user          
                    rkp.save(using=r.session["ccabang"])       
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
                    tambah_rekap.save(using=r.session["ccabang"])
                        
                status = 'ok'

                return JsonResponse({"status": status})
            except Exception as e:
                transaction.set_rollback(True,using=r.session["ccabang"])
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
                raise Exception(msg)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if e.args is not None else "Terjadi kesalahan"
        return JsonResponse({"status":'error',"msg":msg},status=400)


@authorization(["*"])
def kompen_json(r, idp, prd, thn):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest": 
        
        data = []
        
        pa = periode_absen(prd,thn)
        dr = pa[0].date()
        sp = pa[1].date()
        
        for l in kompen_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_kompen__range=(dr,sp)).order_by('tgl_kompen'):
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

@authorization(["*"])
def kompen(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses

        dsid = dakses.sid_id  

        pgw = pegawai_db.objects.using(r.session["ccabang"]).get(userid=iduser)

        # get all jam kerja 
        jk = jamkerja_db.objects.using(r.session["ccabang"]).filter(kk_id=pgw.kelompok_kerja.pk)

        # dt_raw = sorted(draw,key=lambda i: i["jam_absen"])
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        ###
        sid_lembur = 0

        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'status' : status,
            'dsid': dsid,
            'sid': pgw.status_id,
            'sil': sid_lembur,
            "pegawai":pgw,
            'userid':pgw.userid,
            'modul_aktif' : 'Absensi'
            }
            
        return render(r,'hrd_app/kompen/kompen.html', data)


@authorization(["root","it"])
def status_pegawai_lembur(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        if r.session["user"]["admin"]:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
        else:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(divisi__in=aksesdivisi)
        divisi = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=aksesdivisi)
        sids = [s.status_id for s in pegawai.distinct("status_id")]
        status = status_pegawai_db.objects.using(r.session['ccabang']).filter(id__in=sids)
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            "pegawai":pegawai,
            "divisi":divisi,
            "status":status,
            'modul_aktif' : 'Pegawai Lembur'     
        }
        
        return render(r,'hrd_app/status_pegawai/status_pegawai_lembur/status_pegawai_lembur.html', data)
        
    else:    
        messages.error(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["root","it"])
def tstatus_pegawai_lembur(r):
    idp = r.POST.get("idp")
    if idp == "":
        return JsonResponse({'status':'error',"msg":"Pegawai tidak boleh kosong"},safe=False,status=400)

    if list_pegawai_lembur_db.objects.using(r.session["ccabang"]).filter(pegawai_id=idp).exists():
        return JsonResponse({'status':'error',"msg":"Pegawai sudah didaftarkan"},safe=False,status=400)
    else:
        if not pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp)).exists():
            return JsonResponse({'status':'error',"msg":"Pegawai tidak ada"},safe=False,status=400)
        list_pegawai_lembur_db(pegawai_id=int(idp)).save(using=r.session["ccabang"])
        return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)

@authorization(["root","it"])
def tstatus_pegawai_lembur_divisi(r):
    divisi = r.POST.get("divisi")
    if divisi == "":
        return JsonResponse({'status':'error',"msg":"Divisi tidak boleh kosong"},safe=False,status=400)
    
    dvs = divisi_db.objects.using(r.session["ccabang"]).filter(pk=int(divisi)).last()
    if not dvs:
        return JsonResponse({"status":"error","msg":"Divisi tidak ada"},safe=False,status=400)
    

    pgw = [p.pk for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id=dvs)]
    data = []
    for pg in pgw:
        if list_pegawai_lembur_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg).exists():
            continue
        else:
            data.append(list_pegawai_lembur_db(pegawai_id=int(pg)))
    
    list_pegawai_lembur_db.objects.using(r.session['ccabang']).bulk_create(data)

    return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)

@authorization(["root",'it'])
def tstatus_pegawai_lembur_status(r):
    status = r.POST.get("status")
    if status == "":
        return JsonResponse({'status':'error',"msg":"Status tidak boleh kosong"},safe=False,status=400)
    st = status_pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(status)).last()
    if not st:
        return JsonResponse({"status":"error","msg":"Status tidak ada"},safe=False,status=400)
    

    pgw = [p.pk for p in pegawai_db.objects.using(r.session["ccabang"]).filter(status_id=status)]
    data = []
    for pg in pgw:
        if list_pegawai_lembur_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg).exists():
            continue
        else:
            data.append(list_pegawai_lembur_db(pegawai_id=int(pg)))
    
    list_pegawai_lembur_db.objects.using(r.session['ccabang']).bulk_create(data)

    return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)





@authorization(["root","it"])
def status_pegawai_lembur_json(r):
    result = list_pegawai_lembur_db.objects.using(r.session["ccabang"]).all()
    data = []
    for r in result:
        obj = {
            'pegawai':r.pegawai.nama,
            "divisi":r.pegawai.divisi.divisi,
            "status":r.pegawai.status.status,
            'pk':r.pk,
            "pegawai_id":r.pegawai_id
        }
        data.append(obj)
    
    return JsonResponse({"data":data},status=200,safe=False)

@authorization(["root","it"])
def estatus_pegawai_lembur(r):
    idp = r.POST.get("idp")
    id = r.POST.get('id')
    if id == "" or idp == '':
        return JsonResponse({'status':'error',"msg":"Data tidak lengkap"},safe=False,status=400)
    try:
        get = list_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        if list_pegawai_lembur_db.objects.using(r.session["ccabang"]).filter(~Q(pk=int(id)), pegawai_id=int(idp)).exists():
            return JsonResponse({"status":"erorr","msg":"Pegawai sudah didaftarkan"},status=400)
        list_pegawai_lembur_db.objects.using(r.session["ccabang"]).filter(pk=int(id)).update(pegawai_id=int(idp))
        return JsonResponse({'status':'success',"msg":"Berhasil update pegawai"},safe=False,status=200)
    except:
        return JsonResponse({"status":"error","msg":"Terjadi kesalahan"},safe=False,status=400)

@authorization(["root","it"])
def hstatus_pegawai_lembur(r):
    id = r.POST.get('id')
    if id == "":
        return JsonResponse({'status':'error',"msg":"Data tidak lengkap"},safe=False,status=400)
    nama_user = r.session["user"]["nama"]
    try:
        get = list_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus pegawai lembur : {get.pegawai.nama}'
        ).save(using=r.session["ccabang"])
        list_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(pk=int(id)).delete(using=r.session["ccabang"])
        return JsonResponse({'status':'success',"msg":"Berhasil hapus pegawai"},safe=False,status=200)
    except:
        return JsonResponse({"status":"error","msg":"Terjadi kesalahan"},safe=False,status=400)
    



# status pegawai libur nasional




@authorization(["root","it"])
def status_pegawai_libur_nasional(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        if r.session["user"]["admin"]:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
        else:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(divisi__in=aksesdivisi)
        divisi = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=aksesdivisi)
        sids = [s.status_id for s in pegawai.distinct("status_id")]
        status = status_pegawai_db.objects.using(r.session['ccabang']).filter(id__in=sids)
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        print(akses)
        
        data = {       
            'dsid': dsid,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            "divisi":divisi,
            "status":status,
            "pegawai":pegawai,
            'modul_aktif' : 'Pegawai Libur Nasional'     
        }
        
        return render(r,'hrd_app/status_pegawai/status_pegawai_libur_nasional.html', data)
        
    else:    
        messages.error(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

    
    
@authorization(["root","it"])
def tstatus_pegawai_libur_nasional(r):
    idp = r.POST.get("idp")
    if idp == '':
        return JsonResponse({"status":"error","msg":"Data tidak lengkap"},safe=False,status=400)
    if list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).filter(pegawai_id=idp).exists():
        return JsonResponse({'status':'error',"msg":"Pegawai sudah didaftarkan"},safe=False,status=400)
    else:
        if  not pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp)).exists():
            return JsonResponse({'status':'error',"msg":"Pegawai tidak ada"},safe=False,status=400)
        list_pegawai_opg_libur_nasional_db(pegawai_id=int(idp)).save(using=r.session["ccabang"])
        return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)



@authorization(["root","it"])
def tstatus_pegawai_libur_nasional_divisi(r):
    divisi = r.POST.get("divisi")
    if divisi == "":
        return JsonResponse({'status':'error',"msg":"Divisi tidak boleh kosong"},safe=False,status=400)
    
    dvs = divisi_db.objects.using(r.session["ccabang"]).filter(pk=int(divisi)).last()
    if not dvs:
        return JsonResponse({"status":"error","msg":"Divisi tidak ada"},safe=False,status=400)
    

    pgw = [p.pk for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id=dvs)]
    data = []
    for pg in pgw:
        if list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg).exists():
            continue
        else:
            data.append(list_pegawai_opg_libur_nasional_db(pegawai_id=int(pg)))
    
    list_pegawai_opg_libur_nasional_db.objects.using(r.session['ccabang']).bulk_create(data)

    return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)

@authorization(["root",'it'])
def tstatus_pegawai_libur_nasional_status(r):
    status = r.POST.get("status")
    if status == "":
        return JsonResponse({'status':'error',"msg":"Status tidak boleh kosong"},safe=False,status=400)
    st = status_pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(status)).last()
    if not st:
        return JsonResponse({"status":"error","msg":"Status tidak ada"},safe=False,status=400)
    

    pgw = [p.pk for p in pegawai_db.objects.using(r.session["ccabang"]).filter(status_id=status)]
    data = []
    for pg in pgw:
        if list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg).exists():
            continue
        else:
            data.append(list_pegawai_opg_libur_nasional_db(pegawai_id=int(pg)))
    
    list_pegawai_opg_libur_nasional_db.objects.using(r.session['ccabang']).bulk_create(data)

    return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)



@authorization(["root","it"])
def status_pegawai_libur_nasional_json(r):
    result = list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).all()
    data = []
    for r in result:
        obj = {
            'pegawai':r.pegawai.nama,
            "divisi":r.pegawai.divisi.divisi,
            "status":r.pegawai.status.status,
            'pk':r.pk,
            "pegawai_id":r.pegawai_id
        }
        data.append(obj)
    
    return JsonResponse({"data":data},status=200,safe=False)

@authorization(["root","it"])
def estatus_pegawai_libur_nasional(r):
    idp = r.POST.get("idp")
    id = r.POST.get('id')
    if id == "" or idp == '':
        return JsonResponse({'status':'error',"msg":"Data tidak lengkap"},safe=False,status=400)
    try:
        get = list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        if list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).filter(~Q(pk=int(id)), pegawai_id=int(idp)).exists():
            return JsonResponse({"status":"error","msg":"Pegawai sudah didaftarkan"},status=400)
        list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).filter(pk=int(id)).update(pegawai_id=int(idp))
        return JsonResponse({'status':'ok'},safe=False,status=200)
    except Exception as err:
        
        return JsonResponse({"status":"gagal update"},safe=False,status=400)

@authorization(["root","it"])
def hstatus_pegawai_libur_nasional(r):
    id = r.POST.get('id')
    if id == "":
        return JsonResponse({'status':'error',"msg":"Data tidak lengkap"},safe=False,status=400)
    nama_user = r.session["user"]["nama"]
    try:
        get = list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus pegawai libur nasional : {get.pegawai.nama}'
        ).save(using=r.session["ccabang"])
        list_pegawai_opg_libur_nasional_db.objects.using(r.session["ccabang"]).get(pk=int(id)).delete(using=r.session["ccabang"])
        return JsonResponse({'status':'ok'},safe=False,status=200)
    except:
        return JsonResponse({"status":"gagal hapus"},safe=False,status=400)


# status pegawai opg

@authorization(["root","it"])
def status_pegawai_opg(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        if r.session["user"]["admin"]:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
        else:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(divisi__in=aksesdivisi)
        divisi = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=aksesdivisi)
        print(pegawai.distinct("status_id"))
        sids = [s.status_id for s in pegawai.distinct("status_id")]
        status = status_pegawai_db.objects.using(r.session['ccabang']).filter(id__in=sids)
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            "pegawai":pegawai,
            "divisi":divisi,
            "status":status,
            'modul_aktif' : 'Pegawai OPG'     
        }
        
        return render(r,'hrd_app/status_pegawai/status_pegawai_opg.html', data)
        
    else:    
        messages.error(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

    
    
@authorization(["root","it"])
def tstatus_pegawai_opg(r):
    idp = r.POST.get("idp")
    
    if list_pegawai_opg_db.objects.using(r.session["ccabang"]).filter(pegawai_id=idp).exists():
        return JsonResponse({'status':'error',"msg":"Pegawai sudah didaftarkan"},safe=False,status=400)
    else:
        if not pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp)).exists():
            return JsonResponse({'status':'error',"msg":"Pegawai tidak ada"},safe=False,status=400)
        list_pegawai_opg_db(pegawai_id=int(idp)).save(using=r.session["ccabang"])
        return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)
    

@authorization(["root","it"])  
def tstatus_pegawai_opg_divisi(r):
    divisi = r.POST.get("divisi")
    if divisi == "":
        return JsonResponse({'status':'error',"msg":"Divisi tidak boleh kosong"},safe=False,status=400)
    dvs = divisi_db.objects.using(r.session["ccabang"]).filter(pk=int(divisi)).last()
    if not dvs:
        return JsonResponse({"status":"error","msg":"Divisi tidak ada"},safe=False,status=400)
    

    pgw = [p.pk for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id=dvs)]
    data = []
    for pg in pgw:
        if list_pegawai_opg_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg).exists():
            continue
        else:
            data.append(list_pegawai_opg_db(pegawai_id=int(pg)))
    
    list_pegawai_opg_db.objects.using(r.session['ccabang']).bulk_create(data)

    return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)


@authorization(["root","it"])
def tstatus_pegawai_opg_status(r):
    status = r.POST.get("status")
    if status == "":
        return JsonResponse({'status':'error',"msg":"Status tidak boleh kosong"},safe=False,status=400)
    st = status_pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(status)).last()
    if not st:
        return JsonResponse({"status":"error","msg":"Status tidak ada"},safe=False,status=400)
    

    pgw = [p.pk for p in pegawai_db.objects.using(r.session["ccabang"]).filter(status_id=status)]
    data = []
    for pg in pgw:
        if list_pegawai_opg_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg).exists():
            continue
        else:
            data.append(list_pegawai_opg_db(pegawai_id=int(pg)))
    
    list_pegawai_opg_db.objects.using(r.session['ccabang']).bulk_create(data)

    return JsonResponse({'status':'success',"msg":"Berhasil menambahkan pegawai"},safe=False,status=201)




@authorization(["root","it"])
def status_pegawai_opg_json(r):
    result = list_pegawai_opg_db.objects.using(r.session["ccabang"]).all()
    data = []
    for r in result:
        obj = {
            'pegawai':r.pegawai.nama,
            "divisi":r.pegawai.divisi.divisi,
            "status":r.pegawai.status.status,
            'pk':r.pk,
            "pegawai_id":r.pegawai_id
        }
        data.append(obj)
    
    return JsonResponse({"data":data},status=200,safe=False)


@authorization(["root","it"])
def estatus_pegawai_opg(r):
    idp = r.POST.get("idp")
    id = r.POST.get('id')

    try:
        get = list_pegawai_opg_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        if list_pegawai_opg_db.objects.using(r.session["ccabang"]).filter(~Q(pk=int(id)), pegawai_id=int(idp)).exists():
            return JsonResponse({"status":"error","msg":"Pegawai sudah didaftarkan"},status=400)
        list_pegawai_opg_db.objects.using(r.session["ccabang"]).filter(pk=int(id)).update(pegawai_id=int(idp))
        return JsonResponse({'status':'success',"msg":"Berhasil edit pegawai"},safe=False,status=200)
    except Exception as err:
        
        return JsonResponse({"status":"error",'msg':"Terjadi kesalahan"},safe=False,status=400)


@authorization(["root","it"])
def hstatus_pegawai_opg(r):
    id = r.POST.get('id')
    nama_user = r.session["user"]["nama"]
    try:
        get = list_pegawai_opg_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus pegawai opg: {get.pegawai.nama}'
        ).save(using=r.session["ccabang"])
        list_pegawai_opg_db.objects.using(r.session["ccabang"]).get(pk=int(id)).delete(using=r.session["ccabang"])
        return JsonResponse({'status':"success","msg":"Berhasil hapus pegawai"},safe=False,status=200)
    except:
        return JsonResponse({"status":"error","msg":"Terjadi kesalahan"},safe=False,status=400)




def get_jam_kerja(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        tgl = r.POST.get("tgl")
        pegawai = r.POST.get("pegawai")

        if not tgl or not pegawai:
            return JsonResponse({"status":'error',"msg":"harap isi tanggal lembur dan pilh pegawai dengan benar"},status=400)

        if not pegawai_db.objects.using(r.session['ccabang']).filter(pk=int(pegawai)).exists():
            return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
        try:
            date = datetime.strptime(datetime.strftime(datetime.strptime(tgl,"%d-%m-%Y"),"%Y-%m-%d"),"%Y-%m-%d")
            absen = absensi_db.objects.using(r.session["ccabang"]).filter(tgl_absen=date.date(),pegawai_id=pegawai).last()
            if not absen:
                return JsonResponse({"status":"error","msg":"Tidak ada jadwal kerja. Silahkan cek absensi pegawai tersebut"},status=400)
            data = {
                "html":f"{absen.jam_masuk} - {absen.jam_pulang} / Istirahat : {absen.lama_istirahat} Jam",
                "id":absen.pk
            }

            return JsonResponse({"status":"success",'msg':"Berhasil","data":data},status=200)
        except Exception as e:
            return JsonResponse({"status":"error","msg":"Terjadi kesalahan"},status=400)
        

@authorization(["root","it"])
def rp_lembur(r):
    user = r.session["user"]
    akses = akses_db.objects.using(r.session['ccabang']).filter(user_id=user["id"]).last()
    rp = rp_lembur_db.objects.using(r.session['ccabang']).all()
    data = {
        "cabang":r.session["cabang"],
        "ccabang":r.session["ccabang"],
        "dsid":akses.sid_id,
        "data":rp,
        "modul_aktif":"Rupiah Lembur"
    }
    return render(r,"hrd_app/lembur/rp_lembur/rp_lembur.html",data)


@authorization(["root","it"])
def trp_lembur(r):
    rp = r.POST.get("rupiah")
    if rp == "":
        messages.error(r,"Harap isi form dengan lengkap")
        return redirect("rp_lembur")
    try:
        rp = int(rp)
    except Exception as e:
        messages.error(r,"Hanya bisa angka")
        return redirect("rp_lembur")
    rp_lembur_db(rupiah=rp).save(using=r.session['ccabang'])
    messages.success(r,"Berhasil menambahkan rupiah lembur")
    return redirect("rp_lembur")    

@authorization(["root","it"])
def erp_lembur(r):
    id = r.POST.get("edit_id")
    rp = r.POST.get("rupiah")
    if rp == "" or id == "":
        messages.error(r,"Harap isi form dengan lengkap")
        return redirect("rp_lembur")
    try:
        rp = int(rp)
    except Exception as e:
        messages.error(r,"Hanya bisa angka")
        return redirect("rp_lembur")
    print(id,rp)
    rp_lembur_db.objects.using(r.session["ccabang"]).filter(pk=id).update(rupiah=rp)
    messages.success(r,"Berhasil edit rupiah lembur")
    return redirect("rp_lembur")    

@authorization(["root","it"])
def drp_lembur(r):
    id = r.POST.get("hapus_id")
    rp_lembur_db.objects.using(r.session["ccabang"]).filter(pk=id).delete()
    messages.success(r,"Berhasil hapus rupiah lembur")
    return redirect("rp_lembur")    