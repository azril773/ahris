from hrd_app.controllers.lib import *
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# OPG
@login_required
def opg(request, sid):
    iduser = request.user.id
    
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
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
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
        
        return render(request,'hrd_app/opg/[sid]/opg.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_opg(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dr = request.POST.get('ctgl1')
        sp = request.POST.get('ctgl2')
        sid = request.POST.get('sid')
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
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
        
        return render(request,'hrd_app/opg/copg/[dr]/[sp]/[sid]/copg.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_opg_sid(request, dr, sp, sid):
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

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
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
        
        return render(request,'hrd_app/opg/copg/[dr]/[sp]/[sid]/copg.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def opg_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        print(sid)
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        print(dari,sampai)
                
        if int(sid) == 0:
            for i in opg_db.objects.select_related("pegawai","pegawai__divisi").filter(opg_tgl__range=(dari,sampai)):
                
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
            for i in opg_db.objects.select_related("pegawai","pegawai__divisi").filter(opg_tgl__range=(dari,sampai), pegawai__status_id=int(sid)):
                
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
        print(data)       
        return JsonResponse({"data": data})


@login_required
def tambah_opg(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl')
    dpegawai = request.POST.get('pegawai')
    
    tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()   
    
    pg = pegawai_db.objects.get(id=int(dpegawai))  
    off = pg.hari_off.hari
    
    if libur_nasional_db.objects.filter(tgl_libur=tgl).exists():
        ln = libur_nasional_db.objects.get(tgl_libur=tgl)
        tln = ln.tgl_libur
    else:
        tln = None    
    
    day = tgl.strftime("%A")
    nh = nama_hari(day) 
            
    if opg_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), opg_tgl=tgl).exists():
        status = 'duplikat'
    else:        
        
        # cek jika sudah terdapat opg, batalkan
        if geseroff_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), dari_tgl=tgl).exists():
            status = 'ada geseroff'
        else:
            # cek jika absen di tanggal opg tgl tidak ada absen masuk atau absen pulangnya, batalkan
            if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=tgl).exists():
                
                ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=tgl)

                if ab.masuk is None and ab.pulang is None:
                    status = 'pegawai tidak masuk'
                else:
                    if nh == off:
                        print("OSDKOSKDOKD")
                        topg = opg_db(
                            pegawai_id = int(dpegawai),
                            opg_tgl = tgl,
                            keterangan = 'OFF Pengganti Reguler',
                            add_by = nama_user,
                            edit_by = nama_user
                        )
                        topg.save()
                        
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
                                topg.save()
                        
                                status = 'ok'
                            else:
                                status = 'bukan tgl merah'
                        else:
                            status = 'bukan off reguler'   
            else:
                status = 'belum ada data absensi'                                 
                                    
    return JsonResponse({"status": status})


@login_required
def pakai_opg(request):
    nama_user = request.user.username
    
    idopg = request.POST.get('id_pakai')
    dtgl = request.POST.get('ptgl')
    
    diambil_tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()
    
    opg = opg_db.objects.get(id=int(idopg))
    idp = opg.pegawai_id
    opg_tgl = datetime.strftime(opg.opg_tgl,'%d-%m-%Y')   
    
    pg = pegawai_db.objects.get(id=int(idp))  
    off = pg.hari_off.hari
    day = diambil_tgl.strftime("%A")
    nh = nama_hari(day) 
            
    if absensi_db.objects.filter(tgl_absen=diambil_tgl, pegawai_id=int(idp)).exists():
        
        ab = absensi_db.objects.get(tgl_absen=diambil_tgl, pegawai_id=int(idp))
        
        if ab.masuk is None and ab.pulang is None:
            if off == nh:
                status = 'hari off'
            else:
                if geseroff_db.objects.filter(pegawai_id=int(idp), ke_tgl=diambil_tgl).exists():
                    status = 'ada geseroff'
                else:        
                    ab.keterangan_absensi = f"OPG-({opg_tgl})"
                    ab.save()
                    
                    opg.diambil_tgl = diambil_tgl
                    opg.status = 1
                    opg.edit_by = nama_user
                    opg.save()
                    
                    status = 'ok'
        else:
            status = 'pegawai masuk'    
    else:
        status = "data absensi tidak ada"     
    return JsonResponse({"status": status})


@login_required
def batal_opg(request):
    nama_user = request.user.username
    
    idopg = request.POST.get('id_batal')
    
    opg = opg_db.objects.select_related('pegawai').get(id=int(idopg))
    
    idp = opg.pegawai_id
    tgl = opg.diambil_tgl
    
    ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=tgl)
    ab.keterangan_absensi = None
    ab.save()
    
    opg.diambil_tgl = None
    opg.status = 0
    opg.edit_by = nama_user
    opg.save()
    
    status = 'ok'
                                  
    return JsonResponse({"status": status})


@login_required
def hapus_opg(request):
    nama_user = request.user.username
    
    idopg = request.POST.get('id_hapus')
    
    opg = opg_db.objects.select_related('pegawai').get(id=int(idopg))
    idp = opg.pegawai_id
    nama_pegawai = opg.pegawai.nama
    tgl_ambil = opg.diambil_tgl
    tgl_opg = opg.opg_tgl
    
    if opg.status == 1:
        ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=tgl_ambil)
        ab.keterangan_absensi = None
        ab.save()       
    else:
        pass
    
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"OPG-(a.n {nama_pegawai}, tgl:{tgl_opg})"
    )
    histori.save()    
    
    opg.delete()
        
    status = 'ok'
                                  
    return JsonResponse({"status": status})

