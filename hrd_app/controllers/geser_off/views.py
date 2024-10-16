
from hrd_app.controllers.lib import *
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Geser Off
@login_required
def geser_off(request, sid):
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
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/geser_off/[sid]/geser_off.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_geser_off(request):
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
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/geser_off/[dr]/[sp]/[sid]/cgeser_off.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_geser_off_sid(request, dr, sp, sid):
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
            'modul_aktif' : 'Geser OFF'
        }
        
        return render(request,'hrd_app/geser_off/[dr]/[sp]/[sid]/cgeser_off.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def geseroff_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
                
        if int(sid) == 0:
            for i in geseroff_db.objects.filter(dari_tgl__range=(dari,sampai)):
                            
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
            for i in geseroff_db.objects.select_related('pegawai').filter(dari_tgl__range=(dari,sampai), pegawai__status_id=int(sid)):
                            
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
def tambah_geseroff(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl')
    dtgl2 = request.POST.get('tgl2')
    dpegawai = request.POST.get('pegawai')
    dket = request.POST.get('ket')
    
    dari = datetime.strptime(dtgl,'%d-%m-%Y').date()
    ke = datetime.strptime(dtgl2,'%d-%m-%Y').date()   
    
    fdari = datetime.strftime(dari,'%d-%m-%Y')  
    
    pg = pegawai_db.objects.get(id=int(dpegawai))  
    off = pg.hari_off.hari
    if libur_nasional_db.objects.filter(tgl_libur=dari).exists():
        ln = libur_nasional_db.objects.get(tgl_libur=dari)
        tln = ln.tgl_libur
    else:
        tln = None    
    if dari < ke:
        return JsonResponse({"status":"error","msg":"'dari tanggal' tidak boleh lebih kecil dari 'ke tanggal'. Silahkan gunakan opg"},status=400)
    day = dari.strftime("%A")
    nh = nama_hari(day) 
            
    if geseroff_db.objects.select_related('pegawai').filter(Q(dari_tgl=dari)|Q(ke_tgl=ke),pegawai_id=int(dpegawai)).exists():
        status = 'duplikat'
    else:        
        
        # cek jika sudah terdapat opg, batalkan
        if opg_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), opg_tgl=dari).exists():
            status = 'ada opg'
        else:
            # cek jika absen di tanggal dari tgl tidak ada absen masuk atau absen pulangnya, batalkan
            if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=dari).exists():
                ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=dari)
                
                if ab.masuk is not None or ab.pulang is not None:
                    
                    # cek jika absen di tanggal ke tgl ada absen masuk atau absen pulangnya, batalakan
                    if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=ke).exists():
                        ab2 = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=ke)
                        
                        if ab2.masuk is not None and ab.pulang is not None:
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
                                tambahgf.save()
                                
                                ab2.keterangan_absensi = f"Geser OFF-({fdari})"
                                ab2.save()
                                
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
                                        tambahgf.save()
                                        
                                        ab2.keterangan_absensi = f"Geser OFF-({fdari})"
                                        ab2.save()
                                        
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
                            tambahgf.save()
                            
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
                                    tambahgf.save()
                                    
                                    status = 'ok'
                                else:
                                    status = 'bukan tgl merah'
                            else:
                                status = 'bukan hari off'   
                    
                else:
                    status = 'pegawai tidak masuk'  

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
                    tambahgf.save()
                    
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
                            tambahgf.save()
                            
                            status = 'ok'
                        else:
                            status = 'bukan tgl merah'
                    else:
                        status = 'bukan hari off'    
    
                    
    return JsonResponse({"status": status})


@login_required
def batal_geseroff(request):
    nama_user = request.user.username

    id_batal = request.POST.get('id_batal')
    
    gf = geseroff_db.objects.select_related('pegawai').get(id=int(id_batal))
    
    ke_tgl = gf.ke_tgl
    dari_tgl = gf.dari_tgl
    idp = gf.pegawai_id
    nama_pegawai = gf.pegawai.nama
        
    if libur_nasional_db.objects.filter(tgl_libur=dari_tgl).exists():
        ln = libur_nasional_db.objects.get(tgl_libur=dari_tgl)
        tln = ln.tgl_libur
        kopg = 'OFF Pengganti Tgl Merah'
    else:
        tln = None 
        kopg = 'OFF Pengganti Reguler'
    
    ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=ke_tgl)
    ab.keterangan_absensi = None
    ab.save()
    
    if opg_db.objects.filter(pegawai_id=int(idp), opg_tgl=dari_tgl).exists():
        pass
    else:
        tambah_opg = opg_db(
            pegawai_id = int(idp),
            opg_tgl = dari_tgl,  
            keterangan = kopg,          
            add_by = 'Program',
            edit_by = 'Program'
        )
        tambah_opg.save()
       
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"Geser OFF-(a.n {nama_pegawai}, tgl:{dari_tgl})"
    )
    histori.save()
    
    gf.delete()    
    
    status = 'ok'    
    
    return JsonResponse({"status": status})

