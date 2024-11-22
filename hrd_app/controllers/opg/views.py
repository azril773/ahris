from hrd_app.controllers.lib import *
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# OPG
@login_required
def opg(r, sid):
    iduser = r.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
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
            'modul_aktif' : 'OPG'
        }
        
        return render(r,'hrd_app/opg/[sid]/opg.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_opg(r):
    iduser = r.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dr = r.POST.get('ctgl1')
        sp = r.POST.get('ctgl2')
        sid = r.POST.get('sid')
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1):
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
            'modul_aktif' : 'OPG'
        }
        
        return render(r,'hrd_app/opg/copg/[dr]/[sp]/[sid]/copg.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_opg_sid(r, dr, sp, sid):
    iduser = r.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1):
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
            'modul_aktif' : 'OPG'
        }
        
        return render(r,'hrd_app/opg/copg/[dr]/[sp]/[sid]/copg.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def opg_json(r, dr, sp, sid):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)]
        if int(sid) == 0:
            for i in opg_db.objects.using(r.session["ccabang"]).select_related("pegawai","pegawai__divisi").filter(opg_tgl__range=(dari,sampai),pegawai__divisi_id__in=aksesdivisi):
                
                if i.diambil_tgl is not None:
                    dtgl = datetime.strftime(i.diambil_tgl, '%d-%m-%Y')
                else:
                    dtgl = None    
                            
                op = {
                    'id':i.id,
                    'opg_tgl':datetime.strftime(i.opg_tgl, '%d-%m-%Y'),
                    'diambil_tgl':dtgl,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan,
                    'status':i.status
                }
                data.append(op)
        else:
            for i in opg_db.objects.using(r.session["ccabang"]).select_related("pegawai","pegawai__divisi").filter(opg_tgl__range=(dari,sampai), pegawai__status_id=int(sid),pegawai__divisi_id__in=aksesdivisi):
                
                if i.diambil_tgl is not None:
                    dtgl = datetime.strftime(i.diambil_tgl, '%d-%m-%Y')
                else:
                    dtgl = None 
                            
                op = {
                    'id':i.id,
                    'opg_tgl':datetime.strftime(i.opg_tgl, '%d-%m-%Y'),
                    'diambil_tgl':dtgl,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan,
                    'status':i.status
                }
                data.append(op)
        return JsonResponse({"data": data})


@login_required
def tambah_opg(r):
    nama_user = r.user.username
    
    dtgl = r.POST.get('tgl')
    dpegawai = r.POST.get('pegawai')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)]
    tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()   
    try:
        pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=int(dpegawai),divisi_id__in=aksesdivisi)  
    except:
        return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
    off = pg.hari_off.hari
    
    if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur=tgl).exists():
        ln = libur_nasional_db.objects.using(r.session["ccabang"]).get(tgl_libur=tgl)
        tln = ln.tgl_libur
    else:
        tln = None    
    
    day = tgl.strftime("%A")
    nh = nama_hari(day) 
            
    if opg_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").filter(pegawai_id=int(dpegawai), opg_tgl=tgl,pegawai__divisi_id__in=aksesdivisi).exists():
        status = 'duplikat'
    else:        
        
        # cek jika sudah terdapat opg, batalkan
        if geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(dpegawai), dari_tgl=tgl).exists():
            status = 'ada geseroff'
        else:
            # cek jika absen di tanggal opg tgl tidak ada absen masuk atau absen pulangnya, batalkan
            if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=tgl).exists():
                
                ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=tgl)

                if ab.masuk is None and ab.pulang is None:
                    status = 'pegawai tidak masuk'
                else:
                    if nh == off:
                        topg = opg_db(
                            
                            pegawai_id = int(dpegawai),
                            opg_tgl = tgl,
                            keterangan = 'OFF Pengganti Reguler',
                            add_by = nama_user,
                            edit_by = nama_user
                        )
                        topg.save(using=r.session["ccabang"])
                        
                        status = 'ok'
                    else:
                        if tln is not None:
                            if tln == tgl:
                                topg = opg_db(
                                    pegawai_id = int(dpegawai),
                                    opg_tgl = tgl,
                                    keterangan = 'OFF Pengganti Tgl Merah',
                                    add_by = nama_user,
                                    edit_by = nama_user
                                )
                                topg.save(using=r.session["ccabang"])
                        
                                status = 'ok'
                            else:
                                status = 'bukan tgl merah'
                        else:
                            status = 'bukan off reguler'   
            else:
                status = 'belum ada data absensi'                                 
                                    
    return JsonResponse({"status": status})


@login_required
def pakai_opg(r):
    nama_user = r.user.username
    
    idopg = r.POST.get('id_pakai')
    dtgl = r.POST.get('ptgl')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)]
    
    diambil_tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()
    try:
        opg = opg_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").get(id=int(idopg),pegawai__divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":"error","msg":"Opg tidak ada"},status=400)
    idp = opg.pegawai_id
    opg_tgl = datetime.strftime(opg.opg_tgl,'%d-%m-%Y')
    
    try:
        pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=int(idp),divisi_id__in=aksesdivisi)  
    except:
        return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
    off = pg.hari_off.hari
    day = diambil_tgl.strftime("%A")
    nh = nama_hari(day) 
            
    if absensi_db.objects.using(r.session["ccabang"]).filter(tgl_absen=diambil_tgl, pegawai_id=int(idp)).exists():
        
        ab = absensi_db.objects.using(r.session["ccabang"]).get(tgl_absen=diambil_tgl, pegawai_id=int(idp))
        
        if ab.masuk is None and ab.pulang is None:
            if off == nh:
                status = 'hari off'
            else:
                if geseroff_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), ke_tgl=diambil_tgl).exists():
                    status = 'ada geseroff'
                else:        
                    
                    if diambil_tgl < datetime.strptime(opg_tgl,"%d-%m-%Y").date():
                        return JsonResponse({"status":"error","msg":"'diambil tanggal' harus lebih besar dari tanggal opg. Silahkan gunakan geser off"},status=400)
                    ab.keterangan_absensi = f"OPG-({opg_tgl})"
                    ab.save(using=r.session["ccabang"])
                    
                    opg.diambil_tgl = diambil_tgl
                    opg.status = 1
                    opg.edit_by = nama_user
                    opg.save(using=r.session["ccabang"])
                    
                    status = 'ok'
        else:
            status = 'pegawai masuk'    
    else:
        if diambil_tgl < datetime.strptime(opg_tgl,"%d-%m-%Y").date():
            return JsonResponse({"status":"error","msg":"'diambil tanggal' harus lebih besar dari tanggal opg. Silahkan gunakan geser off"},status=400)
        opg.status = 0
        opg.diambil_tgl = diambil_tgl
        opg.edit_by = nama_user
        opg.save(using=r.session["ccabang"])
        status = 'ok'
        # status = "data absensi tidak ada"     
    return JsonResponse({"status": status})


@login_required
def batal_opg(r):
    nama_user = r.user.username
    
    idopg = r.POST.get('id_batal')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)]
    try:
        opg = opg_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(id=int(idopg),pegawai__divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":"error","msg":"Opg tidak ada"},status=400)
    idp = opg.pegawai_id
    tgl = opg.diambil_tgl
    
    ab = absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), tgl_absen=tgl)
    if ab.exists():
        ab[0].keterangan_absensi = None
        ab[0].save(using=r.session["ccabang"])
    
    opg.diambil_tgl = None
    opg.status = 0
    opg.edit_by = nama_user
    opg.save(using=r.session["ccabang"])
    
    status = 'ok'
                                  
    return JsonResponse({"status": status})


@login_required
def hapus_opg(r):
    nama_user = r.user.username
    
    idopg = r.POST.get('id_hapus')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)]
    try:
        opg = opg_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").get(id=int(idopg),pegawai__divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":'error',"msg":"Opg tidak ada"},status=400)
    idp = opg.pegawai_id
    nama_pegawai = opg.pegawai.nama
    tgl_ambil = opg.diambil_tgl
    tgl_opg = opg.opg_tgl
    
    if opg.status == 1:
        try:
            ab = absensi_db.objects.using(r.session["ccabang"]).get(pegawai_id=int(idp), tgl_absen=tgl_ambil)
        except:
            return JsonResponse({"status":'error',"msg":"Tidak ada absensi"},status=400)
        ab.keterangan_absensi = None
        ab.save(using=r.session["ccabang"])       
    else:
        pass
    
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"OPG-(a.n {nama_pegawai}, tgl:{tgl_opg})"
    )
    histori.save(using=r.session["ccabang"])    
    
    opg.delete(using=r.session["ccabang"])
        
    status = 'ok'
                                  
    return JsonResponse({"status": status})

