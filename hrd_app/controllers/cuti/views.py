from hrd_app.controllers.lib import *
from django.db import transaction
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Cuti
@authorization(["*"])
def cuti(r, sid):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = datetime.today()
        pa = periode_skrg()
        dari = datetime.strptime(pa[0].date().strftime("%d-%m-%Y"),"%d-%m-%Y").date()
        sampai = datetime.strptime(pa[1].date().strftime("%d-%m-%Y"),"%d-%m-%Y").date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
        # for pgw in pegawai:
        #     try:
        #         cuti = cuti_db.objects.using(r.session["ccabang"]).filter(pegawai__userid=1265)
        #         cuti = sorted(cuti,key=lambda e: e.tgl_cuti)
        #         ctke = 0
        #         for ct in cuti:
        #             ct.keterangan = f"Cuti ke -{ctke}()"
        #             ct.save(using=r.session["ccabang"])
        #     except Exception as e:
        #         pass
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
            

        ac = awal_cuti_db.objects.using(r.session["ccabang"]).filter().last()
        if not ac:
            return JsonResponse({"status":'error',"msg":"Awal cuti tidak ada"},status=400)
        date = datetime.now().date()
        tglac = ac.tgl + relativedelta(months=10)
        lastday = monthrange(tglac.year,tglac.month)
        tgl = datetime.strptime(f'{tglac.year}-{tglac.month}-{lastday[1]}',"%Y-%m-%d").date()
        updatepgw = []
        for p in pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").filter(aktif=1,divisi_id__in=aksesdivisi):
            if r.session["ccabang"] == "cirebon":
                pgw = pegawai_cuti_lama.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk).last()
                if pgw is not None:
                    obj = {
                        "idp":p.pk,
                        "tgl_cuti":ac.tgl,
                        "expired":tgl,
                        "sisa_cuti":p.sisa_cuti
                    }
                    updatepgw.append(obj)
                else:
                    if p.tgl_masuk is not None:
                        # jika sudah lebih dari satu tahun
                        today = date.today()
                        tmasuk = p.tgl_masuk
                        
                        mkerja = today - tmasuk
                        if int(mkerja.days) > 360:      
                            tgl_masuk = p.tgl_masuk # 2020-01-03
                            today = datetime.now()
                            year = today.year # 2025-01-01
                            tgl_masuk = datetime.strptime(f'{year}-{tgl_masuk.month}-{tgl_masuk.day}',"%Y-%m-%d") # 2025-01-03
                            tgl_cuti = tgl_masuk.date()
                            if today.date() < tgl_masuk.date():
                                new_tglmasuk = tgl_masuk.date() - relativedelta(years=1)
                                tgl_cuti = new_tglmasuk
                                exp = new_tglmasuk + relativedelta(months=10)
                            else:
                                exp = tgl_masuk + relativedelta(months=10)
                            if p.tgl_cuti is not None:
                                if p.tgl_cuti < tgl_cuti:
                                    p.tgl_cuti = tgl_cuti
                                    p.expired = exp
                                    p.sisa_cuti = 12
                                    obj = {
                                        "idp":p.pk,
                                        "tgl_cuti":tgl_cuti,
                                        "expired":exp,
                                        "sisa_cuti":12
                                    }
                                    updatepgw.append(obj)
                                else:
                                    pass
                            else:
                                obj = {
                                    "idp":p.pk,
                                    "tgl_cuti":tgl_cuti,
                                    "expired":exp,
                                    "sisa_cuti":12
                                }
                                updatepgw.append(obj)
                        else:
                            exp = "-"
                    else:
                        exp = "-"

            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid,
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid,
                    }    
                    pegawai.append(data)
                else:
                    pass    
        pegawai_db.objects.using(r.session['ccabang']).bulk_update([pegawai_db(id=dt["idp"],tgl_cuti=dt["tgl_cuti"],expired=dt["expired"],sisa_cuti=dt["sisa_cuti"]) for dt in updatepgw],["tgl_cuti","expired","sisa_cuti"])         
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
            'modul_aktif' : 'Cuti'
        }
        
        return render(r,'hrd_app/cuti/[sid]/cuti.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def detail_cuti(r, sid, idp):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        today = date.today()
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        try:
            pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=int(idp),divisi_id__in=aksesdivisi)
        except:
            messages.error(r,'Pegawai tidak ada')
            return redirect("cuti",sid=sid)
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        
        ac = awal_cuti_db.objects.using(r.session["ccabang"]).filter().last()
        if not ac:
            messages.error(r,"Awal cuti tidak ada")
            return redirect("cuti",sid=sid)
        if r.session["ccabang"] == 'cirebon':
            if pegawai_cuti_lama.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp)).exists():
                tac = ac.tgl       
            else:
                tac = pg.tgl_cuti
        else:
            tac = ac.tgl       
        
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'idp' : idp,
            'dsid': dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari': tac,
            'sampai': today,
            'nama_pegawai':pg.nama,
            'modul_aktif' : 'Cuti'
        }
        
        return render(r,'hrd_app/cuti/[sid]/[idp]/detail_cuti.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def cari_cuti(r):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dtgl1 = r.POST.get('ctgl1')
        dtgl2 = r.POST.get('ctgl2')
        print(dtgl1,dtgl2)
        idp = r.POST.get('idp')
        
        dari = datetime.strptime(dtgl1,'%d-%m-%Y').date()
        sampai = datetime.strptime(dtgl2,'%d-%m-%Y').date()
        
        pg = pegawai_db.objects.using(r.session["ccabang"]).get(id=int(idp))
        sid = pg.status_id      
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'idp' : idp,
            'dsid': dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari': dari,
            'sampai': sampai,
            'nama_pegawai':pg.nama,
            'modul_aktif' : 'Cuti'
        }
        
        return render(r,'hrd_app/cuti/[sid]/[idp]/detail_cuti.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def cuti_json(r, dr, sp, sid):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        if int(sid) == 0:
            for i in cuti_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").filter(tgl_cuti__range=(dari,sampai),pegawai__divisi_id__in=aksesdivisi):
                
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
            for i in cuti_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").filter(tgl_cuti__range=(dari,sampai), pegawai__status_id=int(sid),pegawai__divisi_id__in=aksesdivisi):
                            
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
        print(data)       
        return JsonResponse({"data": data})


@authorization(["*"])
def dcuti_json(r, idp):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        print("OKOOKOK")
        if r.session["ccabang"] == "cirebon":
        
            data = []
            
            ac = awal_cuti_db.objects.using(r.session["ccabang"]).filter().last()
            if not ac:
                return JsonResponse({'status':'error',"msg":"Awal cuti tidak ada "})
            tac = ac.tgl
            aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(idp)).last()
            if not pegawai:
                return JsonResponse({"status":'error',"msg":"Pegawai tidak ada"},status=400)

            pc = pegawai_cuti_lama.objects.using(r.session['ccabang']).filter(pegawai_id=int(idp)).last()
            if pc is not None:
                for i in cuti_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").filter(tgl_cuti__gte=tac, pegawai_id=int(idp),pegawai__divisi_id__in=aksesdivisi):
                                
                    ct = {
                        'id':i.id,
                        'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                        'ket':i.keterangan,
                        'cuti_ke':i.cuti_ke,
                        'edit':i.edit_by,
                        'etgl':datetime.strftime(i.edit_date, '%d-%m-%Y')
                    }
                    data.append(ct) 
            else:
                print(pegawai.tgl_cuti)
                for i in cuti_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").filter(tgl_cuti__gte=pegawai.tgl_cuti, pegawai_id=int(idp),pegawai__divisi_id__in=aksesdivisi):
                                
                    ct = {
                        'id':i.id,
                        'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                        'ket':i.keterangan,
                        'cuti_ke':i.cuti_ke,
                        'edit':i.edit_by,
                        'etgl':datetime.strftime(i.edit_date, '%d-%m-%Y')
                    }
                    data.append(ct) 
            print(data)
        else:
            data = []
            
            ac = awal_cuti_db.objects.using(r.session["ccabang"]).filter().last()
            if not ac:
                return JsonResponse({'status':'error',"msg":"Awal cuti tidak ada "})
            tac = ac.tgl
            aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
            for i in cuti_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").filter(tgl_cuti__gte=tac, pegawai_id=int(idp),pegawai__divisi_id__in=aksesdivisi):                
                ct = {
                    'id':i.id,
                    'tgl_cuti':datetime.strftime(i.tgl_cuti, '%d-%m-%Y'),
                    'ket':i.keterangan,
                    'cuti_ke':i.cuti_ke,
                    'edit':i.edit_by,
                    'etgl':datetime.strftime(i.edit_date, '%d-%m-%Y')
                }
                data.append(ct) 
        print(data)
        return JsonResponse({"data": data})


@authorization(["*"])
def tambah_cuti(r):
    nama_user = r.session["user"]["nama"]
    
    dtgl = r.POST.get('tgl')
    idp = r.POST.get('idp')
    dket = r.POST.get('ket')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
    ltgl = dtgl.split(', ')   
    ac = awal_cuti_db.objects.using(r.session["ccabang"]).last()
    if ac is None:
        return JsonResponse({"status":"error","msg":"Awal cuti tidak ada"})
    tac = ac.tgl
        
    for t in ltgl:
        with transaction.atomic(using=r.session["ccabang"]):
            tgl = datetime.strptime(t,'%d-%m-%Y').date()
            try:
                pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=int(idp),divisi_id__in=aksesdivisi)
            except:
                return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
            if pg.sisa_cuti is not None:
                sc = pg.sisa_cuti
            else:
                return JsonResponse({"status":"error",'msg':"Pegawai tidak memiliki sisa cuti"},status=400)
            
            ct = cuti_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), tgl_cuti__gte=tac).aggregate(total=Count('id'))
            if ct["total"] > 0:
                cuti_ke = ct['total'] + 1  
            else:
                cuti_ke = 1
                
            if dket is None:
                ket = f"Cuti ke {cuti_ke}"
            else:          
                ket = f"Cuti ke {cuti_ke}-({dket})"
    
            # tidak boleh ada opg, geseroff, atau ijin lainnya di tgl yang akan dipakai cuti
            if ijin_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_ijin=tgl).exists():
                status = 'ada ijin'
            else:
                if opg_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), diambil_tgl=tgl).exists():
                    status = 'ada opg' 
                else:
                    if geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), ke_tgl=tgl).exists():
                        status = 'ada geseroff'
                    else:
                        if cuti_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_cuti=tgl).exists():
                            status = 'duplikat'
                        else:
                            if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(idp), tgl_absen=tgl).exists():
                                
                                ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=int(idp), tgl_absen=tgl)
                                
                                if ab.masuk is None and ab.pulang is None:
                                    ab.keterangan_absensi = ket
                                    ab.save(using=r.session["ccabang"])
                                    
                                    tcuti = cuti_db(
                                        pegawai_id = int(idp),
                                        tgl_cuti = tgl,
                                        keterangan = ket,
                                        cuti_ke = cuti_ke,
                                        add_by = nama_user,
                                        edit_by = nama_user
                                    )               
                                    tcuti.save(using=r.session["ccabang"])
                                    sc = sc - 1
                                    if sc < 0:
                                        transaction.set_rollback(True,using=r.session["ccabang"])
                                        return JsonResponse({"status":"error","msg":"Cuti sudah habis"},status=400)
                                    pg.sisa_cuti = sc
                                    pg.save(using=r.session["ccabang"])
                                    
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
                                                ab.save(using=r.session["ccabang"])
                                                
                                                tcuti = cuti_db(
                                                    pegawai_id = int(idp),
                                                    tgl_cuti = tgl,
                                                    keterangan = ket,
                                                    cuti_ke = cuti_ke,
                                                    add_by = nama_user,
                                                    edit_by = nama_user
                                                )               
                                                sc = sc - 1
                                                if sc < 0:
                                                    transaction.set_rollback(True,using=r.session["ccabang"])
                                                    return JsonResponse({"status":"error","msg":"Cuti sudah habis"},status=400)
                                                pg.sisa_cuti = sc
                                                pg.save(using=r.session["ccabang"])
                                                
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
                                                ab.save(using=r.session["ccabang"])
                                                
                                                tcuti = cuti_db(
                                                    pegawai_id = int(idp),
                                                    tgl_cuti = tgl,
                                                    keterangan = ket,
                                                    cuti_ke = cuti_ke,
                                                    add_by = nama_user,
                                                    edit_by = nama_user
                                                )               
                                                tcuti.save(using=r.session["ccabang"])
                                                
                                                sc = sc - 1
                                                if sc < 0:
                                                    transaction.set_rollback(True,using=r.session["ccabang"])
                                                    return JsonResponse({"status":"error","msg":"Cuti sudah habis"},status=400)
                                                pg.sisa_cuti = sc
                                                pg.save(using=r.session["ccabang"])
                                                
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
                                                ab.save(using=r.session["ccabang"])
                                                
                                                tcuti = cuti_db(
                                                    pegawai_id = int(idp),
                                                    tgl_cuti = tgl,
                                                    keterangan = ket,
                                                    cuti_ke = cuti_ke,
                                                    add_by = nama_user,
                                                    edit_by = nama_user
                                                )               
                                                tcuti.save(using=r.session["ccabang"])
                                                
                                                sc = sc - 1
                                                if sc < 0:
                                                    transaction.set_rollback(True,using=r.session["ccabang"])
                                                    return JsonResponse({"status":"error","msg":"Cuti sudah habis"},status=400)
                                                pg.sisa_cuti = sc
                                                pg.save(using=r.session["ccabang"])
                                                
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
                                                ab.save(using=r.session["ccabang"])
                                                
                                                tcuti = cuti_db(
                                                    pegawai_id = int(idp),
                                                    tgl_cuti = tgl,
                                                    keterangan = ket,
                                                    cuti_ke = cuti_ke,
                                                    add_by = nama_user,
                                                    edit_by = nama_user
                                                )               
                                                tcuti.save(using=r.session["ccabang"])
                                                
                                                sc = sc - 1
                                                if sc < 0:
                                                    transaction.set_rollback(True,using=r.session["ccabang"])
                                                    return JsonResponse({"status":"error","msg":"Cuti sudah habis"},status=400)
                                                pg.sisa_cuti = sc
                                                pg.save(using=r.session["ccabang"])
                                                
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
                                tcuti.save(using=r.session["ccabang"])
                                
                                sc = sc - 1
                                if sc < 0:
                                    transaction.set_rollback(True,using=r.session["ccabang"])
                                    return JsonResponse({"status":"error","msg":"Cuti sudah habis"},status=400)
                                pg.sisa_cuti = sc
                                pg.save(using=r.session["ccabang"])
                                
                                status = 'ok'
                                       
    return JsonResponse({"status": status})


@authorization(["*"])
def edit_sisa_cuti(r):
    
    nama_user = r.session["user"]["nama"]

    idp = r.POST.get('idp')
    scuti = r.POST.get('scuti')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    modul = r.POST.get('modul')
    try:
        pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=int(idp),divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":'error',"msg":"Pegawai tidak ada"},status=400)
    
    if modul == 'ecuti':
        pg.sisa_cuti = int(scuti)
        pg.save(using=r.session["ccabang"])
    elif modul == 'reset_cuti':
        pg.sisa_cuti = 12
        pg.save(using=r.session["ccabang"])   
    else:
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1):
            if p.tgl_masuk is None:
                pass
            else:
                pg = pegawai_db.objects.using(r.session["ccabang"]).get(id=p.id)
                
                today = date.today()
                tmasuk = pg.tgl_masuk
                
                mkerja = today - tmasuk
                
                # jika sudah lebih dari satu tahun
                if int(mkerja.days) > 360:                
                    pg.sisa_cuti = 12
                    pg.save(using=r.session["ccabang"])        
                else:
                    pass                         
    
    
    return JsonResponse({"status": "success","msg":"Berhasil edit cuti"})


@authorization(["*"])
def batal_cuti(r):
    nama_user = r.session["user"]["nama"]
    
    idc = r.POST.get('idc')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
    try:
        ct = cuti_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").get(id=int(idc),pegawai__divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":"error","msg":"Cuti tidak ada"},status=400)
    tcuti = ct.tgl_cuti
    idp = ct.pegawai_id
    
    try:
        pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=idp,divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
    if pg.sisa_cuti is not None:
        sc = pg.sisa_cuti
    else:
        return JsonResponse({"status":"error","msg":"Cuti pegawai tidak ada"},status=400)
    
    pg.sisa_cuti = sc + 1
    pg.save(using=r.session["ccabang"]) 
    
    if absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=idp, tgl_absen=tcuti).exists():
        ab = absensi_db.objects.using(r.session["ccabang"]).get(pegawai_id=idp, tgl_absen=tcuti)
        ab.keterangan_absensi = None
        ab.save(using=r.session["ccabang"])
        
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"cuti-(a.n {pg.nama}, tgl:{tcuti})"
    )
    histori.save(using=r.session["ccabang"])   
    
    ct.delete(using=r.session["ccabang"])
    status = "ok"
        
    return JsonResponse({"status": status})