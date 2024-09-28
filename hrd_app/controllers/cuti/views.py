from hrd_app.controllers.lib import *
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Cuti
@login_required
def cuti(request, sid):
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
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/cuti/[sid]/cuti.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def detail_cuti(request, sid, idp):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        today = date.today()
        
        pg = pegawai_db.objects.get(id=int(idp))
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        
        ac = awal_cuti_db.objects.last()
        tac = ac.tgl       
        
        data = {
            'akses' : akses,
            'idp' : idp,
            'dsid': dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari': tac,
            'sampai': today,
            'nama_pegawai':pg.nama,
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/cuti/[sid]/[idp]/detail_cuti.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_cuti(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dtgl1 = request.POST.get('ctgl1')
        dtgl2 = request.POST.get('ctgl2')
        idp = request.POST.get('idp')
        
        dari = datetime.strptime(dtgl1,'%d-%m-%Y').date()
        sampai = datetime.strptime(dtgl2,'%d-%m-%Y').date()
        
        pg = pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id      
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        data = {
            'akses' : akses,
            'idp' : idp,
            'dsid': dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari': dari,
            'sampai': sampai,
            'nama_pegawai':pg.nama,
            'modul_aktif' : 'Cuti'
        }
        
        return render(request,'hrd_app/cuti/[sid]/[idp]/detail_cuti.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cuti_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
                       
        if int(sid) == 0:
            for i in cuti_db.objects.select_related('pegawai',"pegawai__divisi").filter(tgl_cuti__range=(dari,sampai)):
                
                ct = {
                    'id':i.id,
                    'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'sisa_cuti':i.pegawai.sisa_cuti
                }
                data.append(ct)
        else:
            for i in cuti_db.objects.select_related('pegawai',"pegawai__divisi").filter(tgl_cuti__range=(dari,sampai), pegawai__status_id=int(sid)):
                            
                ct = {
                    'id':i.id,
                    'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'sisa_cuti':i.pegawai.sisa_cuti
                }
                data.append(ct)
                               
        return JsonResponse({"data": data})


@login_required
def dcuti_json(request, idp):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        ac = awal_cuti_db.objects.last()
        tac = ac.tgl
        
        for i in cuti_db.objects.select_related('pegawai').filter(tgl_cuti__gte=tac, pegawai_id=int(idp)):
                        
            ct = {
                'id':i.id,
                'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                'ket':i.keterangan,
                'cuti_ke':i.cuti_ke,
                'edit':i.edit_by,
                'etgl':datetime.strftime(i.edit_date, '%d-%m-%Y')
            }
            data.append(ct)
                               
        return JsonResponse({"data": data})


@login_required
def tambah_cuti(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl')
    idp = request.POST.get('idp')
    dket = request.POST.get('ket')
    
    ltgl = dtgl.split(', ')   
    ac = awal_cuti_db.objects.last()
    tac = ac.tgl
        
    for t in ltgl:
        tgl = datetime.strptime(t,'%d-%m-%Y').date()
        
        pg = pegawai_db.objects.get(id=int(idp))
        sc = pg.sisa_cuti
        
        ct = cuti_db.objects.filter(pegawai_id=int(idp), tgl_cuti__gte=tac).aggregate(total=Count('id'))
        if ct is None:
            cuti_ke = 1
        else:
            cuti_ke = ct['total'] + 1  
            
        if dket is None:
            ket = f"Cuti ke {cuti_ke}"
        else:          
            ket = f"Cuti ke {cuti_ke}-({dket})"
   
        # tidak boleh ada opg, geseroff, atau ijin lainnya di tgl yang akan dipakai cuti
        if ijin_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_ijin=tgl).exists():
            status = 'ada ijin'
        else:
            if opg_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), diambil_tgl=tgl).exists():
                status = 'ada opg' 
            else:
                if geseroff_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), ke_tgl=tgl).exists():
                    status = 'ada geseroff'
                else:
                    if cuti_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_cuti=tgl).exists():
                        status = 'duplikat'
                    else:
                        if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(idp), tgl_absen=tgl).exists():
                            
                            ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(idp), tgl_absen=tgl)
                            
                            if ab.masuk is None and ab.pulang is None:
                                ab.keterangan_absensi = ket
                                ab.save()
                                
                                tcuti = cuti_db(
                                    pegawai_id = int(idp),
                                    tgl_cuti = tgl,
                                    keterangan = dket,
                                    cuti_ke = cuti_ke,
                                    add_by = nama_user,
                                    edit_by = nama_user
                                )               
                                tcuti.save()
                                
                                pg.sisa_cuti = sc - 1
                                pg.save()
                                
                                status = 'ok'
                            else:
                                if ab.masuk is not None and ab.pulang is not None:
                                    if ab.masuk < ab.pulang :
                                        dmsk = f'{ab.tgl_absen} {ab.masuk}'
                                        dplg = f'{ab.tgl_absen} {ab.pulang}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                        selisih = datetime.strptime(djam_selisih, '%Y-%m-%d %H:%M:%S')
                                        
                                        if int(selisih.hour) <= 4:
                                            ab.keterangan_absensi = ket
                                            ab.save()
                                            
                                            tcuti = cuti_db(
                                                pegawai_id = int(idp),
                                                tgl_cuti = tgl,
                                                keterangan = ket,
                                                cuti_ke = cuti_ke,
                                                add_by = nama_user,
                                                edit_by = nama_user
                                            )               
                                            tcuti.save()
                                            
                                            pg.sisa_cuti = sc - 1
                                            pg.save()
                                            
                                            status = 'ok'
                                        else:                                
                                            status = 'pegawai masuk'
                                    else:
                                        tplus = ab.tgl_absen         
                            
                                        dmsk = f'{ab.tgl_absen} {ab.masuk}'
                                        dplg = f'{tplus} {ab.pulang}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
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
                                        selisih = datetime.strptime(str(adjusted_datetime), '%Y-%m-%d %H:%M:%S')
                                        
                                        if int(selisih.hour) <= 4: 
                                            ab.keterangan_absensi = ket
                                            ab.save()
                                            
                                            tcuti = cuti_db(
                                                pegawai_id = int(idp),
                                                tgl_cuti = tgl,
                                                keterangan = ket,
                                                cuti_ke = cuti_ke,
                                                add_by = nama_user,
                                                edit_by = nama_user
                                            )               
                                            tcuti.save()
                                            
                                            pg.sisa_cuti = sc - 1
                                            pg.save()
                                            
                                            status = 'ok'
                                        else:
                                            status = 'pegawai masuk'  
                                elif ab.masuk_b is not None and ab.pulang_b is not None:
                                    if ab.masuk_b < ab.pulang_b :
                                        dmsk = f'{ab.tgl_absen} {ab.masuk_b}'
                                        dplg = f'{ab.tgl_absen} {ab.pulang_b}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
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
                                        selisih = datetime.strptime(str(adjusted_datetime), '%Y-%m-%d %H:%M:%S')
                                        
                                        if int(selisih.hour) <= 4:
                                            ab.keterangan_absensi = ket
                                            ab.save()
                                            
                                            tcuti = cuti_db(
                                                pegawai_id = int(idp),
                                                tgl_cuti = tgl,
                                                keterangan = ket,
                                                cuti_ke = cuti_ke,
                                                add_by = nama_user,
                                                edit_by = nama_user
                                            )               
                                            tcuti.save()
                                            
                                            pg.sisa_cuti = sc - 1
                                            pg.save()
                                            
                                            status = 'ok'
                                        else:                                
                                            status = 'pegawai masuk'
                                    else:
                                        tplus = ab.tgl_absen         
                            
                                        dmsk = f'{ab.tgl_absen} {ab.masuk_b}'
                                        dplg = f'{tplus} {ab.pulang_b}'
                                        
                                        msk = datetime.strptime(dmsk, '%Y-%m-%d %H:%M:%S')
                                        plg = datetime.strptime(dplg, '%Y-%m-%d %H:%M:%S')
                                        
                                        dselisih = plg - msk
                                        djam_selisih = f'{ab.tgl_absen} {dselisih}'
                                        selisih = datetime.strptime(str(djam_selisih), '%Y-%m-%d %H:%M:%S')
                                        
                                        if int(selisih.hour) <= 4: 
                                            ab.keterangan_absensi = ket
                                            ab.save()
                                            
                                            tcuti = cuti_db(
                                                pegawai_id = int(idp),
                                                tgl_cuti = tgl,
                                                keterangan = ket,
                                                cuti_ke = cuti_ke,
                                                add_by = nama_user,
                                                edit_by = nama_user
                                            )               
                                            tcuti.save()
                                            
                                            pg.sisa_cuti = sc - 1
                                            pg.save()
                                            
                                            status = 'ok'
                                        else:
                                            status = 'pegawai masuk'  
                                else:
                                    status = 'pegawai masuk'
                        else:
                            tcuti = cuti_db(
                                pegawai_id = int(idp),
                                tgl_cuti = tgl,
                                keterangan = ket,
                                cuti_ke = cuti_ke,
                                add_by = nama_user,
                                edit_by = nama_user
                            )               
                            tcuti.save()
                            
                            pg.sisa_cuti = sc - 1
                            pg.save()
                            
                            status = 'ok'
                                       
    return JsonResponse({"status": status})


@login_required
def edit_sisa_cuti(request):
    
    nama_user = request.user.username
    
    idp = request.POST.get('idp')
    scuti = request.POST.get('scuti')
    modul = request.POST.get('modul')
    
    if modul == 'ecuti':
        pg = pegawai_db.objects.get(id=int(idp))
        pg.sisa_cuti = int(scuti)
        pg.save()
    elif modul == 'reset_cuti':
        pg = pegawai_db.objects.get(id=int(idp))
        pg.sisa_cuti = 12
        pg.save()   
    else:
        for p in pegawai_db.objects.filter(aktif=1):
            if p.tgl_masuk is None:
                pass
            else:
                pg = pegawai_db.objects.get(id=p.id)
                
                today = date.today()
                tmasuk = pg.tgl_masuk
                
                mkerja = today - tmasuk
                
                # jika sudah lebih dari satu tahun
                if int(mkerja.days) > 360:                
                    pg.sisa_cuti = 12
                    pg.save()        
                else:
                    pass                         
    
    status = 'ok'
    
    return JsonResponse({"status": status})


@login_required
def batal_cuti(request):
    nama_user = request.user.username
    
    idc = request.POST.get('idc')
    
    ct = cuti_db.objects.get(id=int(idc))
    tcuti = ct.tgl_cuti
    idp = ct.pegawai_id
    
    pg = pegawai_db.objects.get(id=idp)
    sc = pg.sisa_cuti
    
    pg.sisa_cuti = sc + 1
    pg.save() 
    
    if absensi_db.objects.filter(pegawai_id=idp, tgl_absen=tcuti).exists():
        ab = absensi_db.objects.get(pegawai_id=idp, tgl_absen=tcuti)
        ab.keterangan_absensi = None
        ab.save()
        
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"cuti-(a.n {pg.nama}, tgl:{tcuti})"
    )
    histori.save()   
    
    ct.delete()
    status = "ok"
        
    return JsonResponse({"status": status})

