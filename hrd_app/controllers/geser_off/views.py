
from hrd_app.controllers.lib import *
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Geser Off
@login_required
def geser_off(r, sid):
    iduser = r.user.id
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today().strftime("%Y-%m-%d")
        pa = periode_tgl(today)
        dari = pa[0].date()
        sampai = pa[1].date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi).distinct("status_id"):
            statusid.append(p.status_id)
            # print(p)
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").filter(aktif=1,divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
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
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(r,'hrd_app/geser_off/[sid]/geser_off.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_geser_off(r):
    iduser = r.user.id
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dr = r.POST['ctgl1']
        sp = r.POST['ctgl2']
        sid = r.POST.get('sid')
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi).distinct("status_id"):
            statusid.append(p.status_id)
            # print(p)
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").filter(aktif=1,divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
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
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(r,'hrd_app/geser_off/[dr]/[sp]/[sid]/cgeser_off.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_geser_off_sid(r, dr, sp, sid):
    iduser = r.user.id
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi).distinct("status_id"):
            statusid.append(p.status_id)
            # print(p)
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").filter(aktif=1,divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
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
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(r,'hrd_app/geser_off/[dr]/[sp]/[sid]/cgeser_off.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def geseroff_json(r, dr, sp, sid):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)]  
        if int(sid) == 0:
            for i in geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(dari_tgl__range=(dari,sampai),pegawai__divisi_id__in=aksesdivisi):
                            
                gf = {
                    'id':i.id,
                    'dari_tgl':datetime.strftime(i.dari_tgl, '%d-%m-%Y'),
                    'ke_tgl':datetime.strftime(i.ke_tgl, '%d-%m-%Y'),
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan
                }
                data.append(gf)
        else:
            for i in geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').filter(dari_tgl__range=(dari,sampai), pegawai__status_id=int(sid),pegawai__divisi_id__in=aksesdivisi):
                            
                gf = {
                    'id':i.id,
                    'dari_tgl':datetime.strftime(i.dari_tgl, '%d-%m-%Y'),
                    'ke_tgl':datetime.strftime(i.ke_tgl, '%d-%m-%Y'),
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan
                }
                data.append(gf)
                               
        return JsonResponse({"data": data})


@login_required
def tambah_geseroff(r):
    nama_user = r.user.username
    
    dtgl = r.POST.get('tgl')
    dtgl2 = r.POST.get('tgl2')
    dpegawai = r.POST.get('pegawai')
    dket = r.POST.get('ket')
    
    dari = datetime.strptime(dtgl,'%d-%m-%Y').date()
    ke = datetime.strptime(dtgl2,'%d-%m-%Y').date()   
    
    fdari = datetime.strftime(dari,'%d-%m-%Y')  
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)] 
    try:
        pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=int(dpegawai),divisi_id__in=aksesdivisi)  
    except:
        return JsonResponse({"status":"error","msg":"Data pegawai tidak ada"},status=400)
    off = pg.hari_off.hari
    if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur=dari).exists():
        ln = libur_nasional_db.objects.using(r.session["ccabang"]).get(tgl_libur=dari)
        tln = ln.tgl_libur
    else:
        tln = None    
    if dari < ke:
        return JsonResponse({"status":"error","msg":"'dari tanggal' tidak boleh lebih kecil dari 'ke tanggal'. Silahkan gunakan opg"},status=400)
    day = dari.strftime("%A")
    nh = nama_hari(day) 
            
    if geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(Q(dari_tgl=dari)|Q(ke_tgl=ke),pegawai_id=int(dpegawai)).exists():
        status = 'duplikat'
    else:        
        
        # cek jika sudah terdapat opg, batalkan
        if opg_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(dpegawai), opg_tgl=dari).exists():
            status = 'ada opg'
        else:
            # cek jika absen di tanggal dari tgl tidak ada absen masuk atau absen pulangnya, batalkan
            if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=dari).exists():
                ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=dari)
                                    
                    # cek jika absen di tanggal ke tgl ada absen masuk atau absen pulangnya, batalakan
                if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=ke).exists():
                    ab2 = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=ke)
                    
                    if ab2.masuk is not None and ab2.pulang is not None:
                        status = 'pegawai masuk'
                    else:
                        if off == nh:
                            tambahgf = geseroff_db(
                                pegawai_id = int(dpegawai),
                                dari_tgl = dari,
                                ke_tgl = ke,
                                keterangan = dket,
                                add_by = nama_user,
                                edit_by = nama_user
                            )
                            tambahgf.save(using=r.session["ccabang"])
                            
                            ab2.keterangan_absensi = f"Geser OFF-({fdari})"
                            ab.keterangan_absensi = None
                            ab.save(using=r.session["ccabang"])
                            ab2.save(using=r.session["ccabang"])
                            
                            status = 'ok'
                        else:
                            if tln is not None:
                                if dari == tln:
                                    tambahgf = geseroff_db(
                                        pegawai_id = int(dpegawai),
                                        dari_tgl = dari,
                                        ke_tgl = ke,
                                        keterangan = dket,
                                        add_by = nama_user,
                                        edit_by = nama_user
                                    )
                                    tambahgf.save(using=r.session["ccabang"])
                                    
                                    ab2.keterangan_absensi = f"Geser OFF-({fdari})"
                                    ab.keterangan_absensi = None
                                    ab.save(using=r.session["ccabang"])
                                    ab2.save(using=r.session["ccabang"])
                                    
                                    status = 'ok'
                                else:
                                    status = 'bukan tgl merah'    
                            else:
                                status = 'bukan hari off'
                else:
                    if off == nh:
                        tambahgf = geseroff_db(
                            pegawai_id = int(dpegawai),
                            dari_tgl = dari,
                            ke_tgl = ke,
                            keterangan = dket,
                            add_by = nama_user,
                            edit_by = nama_user
                        )
                        tambahgf.save(using=r.session["ccabang"])
                        
                        status = 'ok'
                    else:
                        if tln is not None:
                            if dari == tln:
                                tambahgf = geseroff_db(
                                    pegawai_id = int(dpegawai),
                                    dari_tgl = dari,
                                    ke_tgl = ke,
                                    keterangan = dket,
                                    add_by = nama_user,
                                    edit_by = nama_user
                                )
                                tambahgf.save(using=r.session["ccabang"])
                                
                                status = 'ok'
                            else:
                                status = 'bukan tgl merah'
                        else:
                            status = 'bukan hari off'   
                    
                # else:
                #     status = 'pegawai tidak masuk'  

            else:
                if off == nh:
                    tambahgf = geseroff_db(
                        pegawai_id = int(dpegawai),
                        dari_tgl = dari,
                        ke_tgl = ke,
                        keterangan = dket,
                        add_by = nama_user,
                        edit_by = nama_user
                    )
                    tambahgf.save(using=r.session["ccabang"])
                    
                    status = 'ok'
                else:
                    if tln is not None:
                        if dari == tln:
                            tambahgf = geseroff_db(
                                pegawai_id = int(dpegawai),
                                dari_tgl = dari,
                                ke_tgl = ke,
                                keterangan = dket,
                                add_by = nama_user,
                                edit_by = nama_user
                            )
                            tambahgf.save(using=r.session["ccabang"])
                            
                            status = 'ok'
                        else:
                            status = 'bukan tgl merah'
                    else:
                        status = 'bukan hari off'    
    
                    
    return JsonResponse({"status": status})


@login_required
def batal_geseroff(r):
    nama_user = r.user.username

    id_batal = r.POST.get('id_batal')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)] 
    try:
        gf = geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").get(id=int(id_batal),pegawai__divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":"error","msg":"Geser off tidak ada"},status=400)
    ke_tgl = gf.ke_tgl
    dari_tgl = gf.dari_tgl
    idp = gf.pegawai_id
    nama_pegawai = gf.pegawai.nama
        
    if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur=dari_tgl).exists():
        ln = libur_nasional_db.objects.using(r.session["ccabang"]).get(tgl_libur=dari_tgl)
        tln = ln.tgl_libur
        kopg = 'OFF Pengganti Tgl Merah'
    else:
        tln = None 
        kopg = 'OFF Pengganti Reguler'
    

    ab = absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), tgl_absen=ke_tgl)
    ab_dari = absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), tgl_absen=dari_tgl)
    if ab.exists():
        ab[0].keterangan_absensi = None
        ab[0].save(using=r.session["ccabang"])
    if ab_dari.exists():
        if (ab_dari[0].masuk is not None and ab_dari[0].pulang is not None) or (ab_dari[0].masuk_b is not None and ab_dari[0].pulang_b is not None):
            if opg_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), opg_tgl=dari_tgl).exists():
                pass
            else:
                tambah_opg = opg_db(
                    pegawai_id = int(idp),
                    opg_tgl = dari_tgl,  
                    keterangan = kopg,          
                    add_by = 'Program',
                    edit_by = 'Program'
                )
                tambah_opg.save(using=r.session["ccabang"])
        else:
            pass
        ab_dari[0].keterangan_absensi = "OFF"
        ab_dari[0].save(using=r.session["ccabang"])
    else:
        pass
       
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"Geser OFF-(a.n {nama_pegawai}, tgl:{dari_tgl})"
    )
    histori.save(using=r.session["ccabang"])
    
    gf.delete(using=r.session["ccabang"])    
    
    status = 'ok'    
    
    return JsonResponse({"status": status})

