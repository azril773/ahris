from hrd_app.controllers.lib import *

@login_required
def amesin(r):
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        mesin = mesin_db.objects.using(r.session["ccabang"]).all()
        data = {       
            'dsid': dsid,
            "mesin":mesin,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'modul_aktif' : 'Counter'     
        }
        
        return render(r,'hrd_app/mesin/mesin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    
@login_required
def mesin_json(r):
    if r.headers["X-Requested-With"] == 'XMLHttpRequest':
        mesin = mesin_db.objects.using(r.session["ccabang"]).all()
        data = []
        for m in mesin:
            obj = {
                "id":m.pk,
                "nama":m.nama,
                "ipaddress":m.ipaddress,
                "status":m.status
            }
            data.append(obj)
        return JsonResponse({"data":data})
    

@login_required
def admesin(r,id): 
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        mesin = mesin_db.objects.using(r.session["ccabang"]).all()
        id = int(id)
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(pk=id)
        dmesin = []
        bmesin = []
        datamesin = datamesin_db.objects.using(r.session["ccabang"]).all()
        dm = []
        for p in datamesin:
            dm.append(p.userid)
        if mesin.exists():
            try:
                zk = ZK(mesin[0].ipaddress,4370,timeout=5)
                conn = zk.connect()
                conn.disable_device()
                users = conn.get_users()


                muserid = [u.user_id for u in users]
                userid = [{"userid":u.user_id,"uid":u.uid} for u in users if u.user_id not in dm]

                conn.enable_device() 
            except Exception as e:
                messages.error(r,"Proccess terminate: {}".format(e))
            finally:
                conn.disconnect()


        data = {       
            'dsid': dsid,
            "mesin":mesin,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'id':id,
            'userid':userid,
            'modul_aktif' : 'Counter'
        }

        
        
        return render(r,'hrd_app/mesin/dmesin.html',data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def rmesin(r,userid,id,uid):
    iduser = r.user.id

    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id

        counter = counter_db.objects.using(r.session["ccabang"]).all().order_by('counter')
        divisi = divisi_db.objects.using(r.session["ccabang"]).all().order_by('divisi')
        jabatan = jabatan_db.objects.using(r.session["ccabang"]).all().order_by('jabatan')
        kk = kelompok_kerja_db.objects.using(r.session["ccabang"]).all().order_by('kelompok')
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('status')
        hr = hari_db.objects.using(r.session["ccabang"]).all()

        kota_kabupaten = kota_kabupaten_db.objects.using(r.session["ccabang"]).all()
        userid = userid
        
        
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'dsid': dsid,
            "counter":counter,
            "divisi":divisi,
            "jabatan":jabatan,
            'status':status,
            "kota_kabupaten":kota_kabupaten,
            "kk":kk,
            "hr":hr,
            "userid":userid,
            "id":id,
            "uid":uid
        }
    return render(r,"hrd_app/mesin/rmesin.html",data)



@login_required
def tambah_data_pegawai(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        user = akses_db.objects.using(r.session["ccabang"]).filter(user_id=r.user.id)
        if not user.exists():
            return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses"},status=400)
        user = user[0]
        sid = user.sid_id
        nama = r.POST.get("nama")
        gender = r.POST.get("gender")
        tgl_masuk = r.POST.get("tgl_masuk")
        nik = r.POST.get("nik")
        userid = r.POST.get("userid")
        uid = r.POST.get("uid")
        id = r.POST.get("id")
        status = r.POST.get("status")
        div = r.POST.get("div")
        counter = r.POST.get("counter")
        jabatan = r.POST.get("jabatan")
        kk = r.POST.get("kk")
        hr = r.POST.get("hr")
        ca = r.POST.get("ca")
        rek = r.POST.get("rek")
        payroll = r.POST.get("payroll")
        nks = r.POST.get("nks")
        ntk = r.POST.get("ntk")
        pks = r.POST.get("pks")
        ptk = r.POST.get("ptk")

        if nama == '' or gender == '' or tgl_masuk == 'Invalid date' or tgl_masuk == '' or nik == '' or userid == '' or div == '' or status == '' or kk == '' or hr == '' or ca == '' or payroll == '':
            return JsonResponse({"status":"error", "msg":"form yang harus diisi tidak boleh kosong"},status=400)

        # Data Pribadi
        alamat = r.POST.get("alamat")
        phone = r.POST.get("phone")
        email = r.POST.get("email")
        kota_lahir = r.POST.get("kota_lahir")
        tgl_lahir = r.POST.get("tgl_lahir")
        tinggi = r.POST.get("tinggi")
        berat = r.POST.get("berat")
        goldarah = r.POST.get("goldarah")
        agama = r.POST.get("agama")


        keluarga = r.POST.get("keluarga")
        pihak = r.POST.get("pihak")
        pengalaman = r.POST.get("pengalaman")
        pendidikan = r.POST.get("pendidikan")
        if keluarga:
            keluarga = json.loads(keluarga)
        else:
            keluarga = []
        

        if pihak:
            pihak = json.loads(pihak)
        else:
            pihak = []


        if pengalaman:
            pengalaman = json.loads(pengalaman)
        else:
            pengalaman = []
        

        if pendidikan:
            pendidikan = json.loads(pendidikan)
        else:
            pendidikan = []
        try:
            status_pegawai = status_pegawai_db.objects.using(r.session["ccabang"]).get(pk=status)
        except:
            status_pegawai = None

        try:
                mesin = mesin_db.objects.using(r.session["ccabang"]).filter(id=int(id))
                conn = ZK(mesin[0].ipaddress,port=4370)
                conn.connect()
                conn.disable_device()


                # users = conn.get_user_template(uid=int(uid))
                users = conn.get_users()
                users = [user for user in users if user.user_id == userid]
                if len(users) <= 0:
                    return JsonResponse({"status":"error","msg":"Userid tidak valid"},status=400)
                    
                if len(users) > 0:
                    datamesin = datamesin_db.objects.using(r.session["ccabang"]).filter(userid=users[0].user_id)
                    if datamesin.exists():
                        return JsonResponse({"status":"error","msg":"Userid sudah ada di datamesin"},status=400)

                    level = 0
                    fingers = []
                    for i in range(1,11):
                        ft = conn.get_user_template(uid=int(users[0].uid),temp_id=i)
                        if ft is not None:
                            fingers.append(ft)                        

                    for f in fingers:
                        sidikjari_db.objects.using(r.session["ccabang"]).filter(uid=f.uid,fid=f.fid).delete()
                        sidikjari_db(
                            uid=f.uid,
                            nama=nama,
                            userid=users[0].user_id,
                            size=f.size,
                            fid=f.fid,
                            valid=f.valid,
                            template=f.template
                        ).save(using=r.session["ccabang"])
                    datamesin_db(
                        uid=users[0].uid,
                        nama=nama,
                        userid=users[0].user_id,
                        level=level
                    ).save(using=r.session["ccabang"])
                conn.enable_device()

        except Exception as e:
            return JsonResponse({"status":"error","msg":e},status=500)
        finally:
            if conn:
                conn.disconnect()
        if alamat == '' or  phone == '' or kota_lahir == '' or tgl_lahir == 'Invalid date' or tgl_lahir == '' or agama == '':
            return JsonResponse({'status':"error","msg":"data pribadi tidak boleh kosong"},status=400,safe=False)
        if email != "":
            if pribadi_db.objects.using(r.session["ccabang"]).filter(email=email).exists():
                return JsonResponse({"status":"error","msg":"Email sudah ada"},status=400)

        if pegawai_db.objects.using(r.session["ccabang"]).filter(userid=userid).exists():
            return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
        else:
            pegawai_db(
                nama=nama,
                gender=gender,
                userid=userid,
                status=status_pegawai,
                nik=nik,
                divisi_id=div,
                jabatan_id=jabatan,
                no_rekening=rek,
                no_bpjs_ks=nks,
                no_bpjs_tk=ntk,
                payroll_by=payroll,
                ks_premi=pks,
                tk_premi=ptk,
                aktif=1,
                tgl_masuk=datetime.strptime(str(tgl_masuk),'%d-%m-%Y').strftime("%Y-%m-%d"),
                tgl_aktif=datetime.now().strftime('%Y-%m-%d'),
                hari_off_id=hr,
                kelompok_kerja_id=kk,
                sisa_cuti=12,
                counter_id=counter,
                add_by=r.user.username,
                edit_by=r.user.username

                # status
            ).save(using=r.session["ccabang"])


            # Tambah Pihak Lain
            pgw = pegawai_db.objects.using(r.session["ccabang"]).get(userid=userid)
            for p in pihak:
                kontak_lain_db(
                    pegawai_id=int(pgw.pk),
                    hubungan = p['hubungan'],
                    nama = p['nama'],
                    gender = p['gender'],
                    phone = p['phone']
                ).save(using=r.session["ccabang"])
            

            # Tambah Keluarga
            for k in keluarga:
                keluarga_db(
                    pegawai_id=int(pgw.pk),
                    hubungan = k['hubungan'],
                    nama = k["nama_keluarga"],
                    tgl_lahir = datetime.strptime(k['tgl_lahir_keluarga'],'%d-%m-%Y'),
                    gender = k['gender'],
                    gol_darah = k['goldarah']
                ).save(using=r.session["ccabang"])

            # Tambah Data Pribadi
            pribadi_db(
                pegawai_id=int(pgw.pk),
                alamat=alamat,
                phone=phone,
                email=email,
                kota_lahir=kota_lahir,
                tgl_lahir=datetime.strptime(tgl_lahir,"%d-%m-%Y").strftime("%Y-%m-%d"),
                tinggi_badan=tinggi if tinggi != "" else 0,
                berat_badan=berat if berat != "" else 0,
                gol_darah=goldarah,
                agama=agama
            ).save(using=r.session["ccabang"])
            for pgl in pengalaman:
                pengalaman_db(
                    pegawai_id=int(pgw.pk),
                    perusahaan=pgl['perusahaan'],
                    kota_id=pgl['kota'],
                    dari_tahun=datetime.strptime(pgl['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pgl['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jabatan=pgl['jabatan']
                ).save(using=r.session["ccabang"])
            
            for pdk in pendidikan:
                pendidikan_db(
                    pegawai_id=int(pgw.pk),
                    pendidikan=pdk['pendidikan'],
                    nama=pdk['nama'],
                    kota_id=pdk['kota'],
                    dari_tahun=datetime.strptime(pdk['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pdk['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jurusan=pdk['jurusan'],
                    gelar=pdk['gelar']
                ).save(using=r.session["ccabang"])
            status = "ok"
            user = r.user.username

            
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)




@login_required
def datamesin(r):
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'id':id,
            'modul_aktif' : 'Counter'
        }
        
        
        return render(r,'hrd_app/mesin/datamesin.html',data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@login_required
def add_data(r,id):
    user = r.user.username

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses   
    try:
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(id=int(id))
        conn = ZK(mesin[0].ipaddress,port=4370)
        conn.connect()
        conn.disable_device()


        fingers = conn.get_templates()
        users = conn.get_users()


        datamesin = [i.userid for i in datamesin_db.objects.using(r.session["ccabang"]).all()]
        userids = [user.user_id for user in users if user.user_id not in datamesin]
        user = [user for user in users if user.user_id not in datamesin]
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(userid__in=userids)
        pegawai_arsip = pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(userid__in=userids)
        # pegawai = [pgw for pgw in pegawai if pgw.userid in userids]
        # 
        for u in user:
            for pgw in pegawai:
                if pgw.userid == u.user_id:
                    if u.privilege == const.USER_ADMIN:
                        level = 1
                    else:
                        level = 0
                    datamesin_db(
                        uid=u.uid,
                        nama=pgw.nama,
                        userid=u.user_id,
                        level=level
                    ).save(using=r.session["ccabang"])
            for pgwa in pegawai_arsip:
                if pgwa.userid == u.user_id:
                    if u.privilege == const.USER_ADMIN:
                        level = 1
                    else:
                        level = 0
                    datamesin_db(
                        uid=u.uid,
                        nama=pgwa.nama,
                        userid=u.user_id,
                        level=level
                    ).save(using=r.session["ccabang"])

        conn.enable_device()

    except Exception as e:
        messages.error(r, "Process terminate : {}".format(e))
    finally:
        if conn:
            conn.disconnect()
    return redirect("amesin")


@login_required
def cdatamesin(r):
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        mesin = mesin_db.objects.using(r.session["ccabang"]).all()
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1)
        divisi = divisi_db.objects.using(r.session["ccabang"]).all()
        data = {       
            'dsid': dsid,
            "mesin":mesin,
            "pegawai":pegawai,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "divisi":divisi,
            'modul_aktif' : 'Mesin'     
        }
        
        return render(r,'hrd_app/mesin/cdatamesin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cpalldata(r):
    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        master = r.POST.get("mesin")
        # divisi = r.POST.getlist("divisi[]")
        mesin_tujuan = r.POST.getlist("mesint[]")
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1)
        
        datauser = []

        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=master)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()


            datamesin = conn.get_users()
            fingers = []
            for dm in datamesin:
                for pgw in pegawai:
                    if dm.user_id == pgw.userid:
                        datauser.append(dm)
            
            for du in datauser:
                for i in range(1,11):
                    ft = conn.get_user_template(uid=du.uid,temp_id=i)
                    if ft is not None:
                        fingers.append(ft)
            conn.enable_device()
        except Exception as e:
            messages.error(r,"Process terminate : {}".format(e))
        finally:
            if conn:
                conn.disconnect()


        
        for m in mesin_tujuan:
            try:
                mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=m)
                zk = ZK(mesin.ipaddress,4370)
                conn = zk.connect()
                conn.disable_device()
                for du in datauser:
                    conn.delete_user(user_id=du.user_id)
                    fts = []
                    for f in fingers:
                        if f.uid == du.uid:
                            fts.append(f)
                    conn.save_user_template(du,fts)        
                conn.enable_device()
            except Exception as e:
                messages.error(r,"Proccess terminate : {}".format(e))
            finally:
                if conn:
                    conn.disconnect()

    return redirect("cdatamesin")

@login_required
def cppegawai(r):
    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        master = r.POST.get("mesin")
        pegawai = r.POST.getlist("pegawai[]")
        mesin_tujuan = r.POST.getlist("mesint[]")
        if len(pegawai) <= 0:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1)
        else:
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=pegawai,aktif=1)
        
        datauser = []

        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=master)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()


            datamesin = conn.get_users()
            fingers = []
            for dm in datamesin:
                for pgw in pegawai:
                    if dm.user_id == pgw.userid:
                        datauser.append(dm)
            
            for du in datauser:
                for i in range(1,11):
                    ft = conn.get_user_template(uid=du.uid,temp_id=i)
                    if ft is not None:
                        fingers.append(ft)
            conn.enable_device()
        except Exception as e:
            messages.error(r,"Process terminate : {}".format(e))
        finally:
            if conn:
                conn.disconnect()


        
        for m in mesin_tujuan:
            try:
                mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=m)
                zk = ZK(mesin.ipaddress,4370)
                conn = zk.connect()

                conn.disable_device()


                for du in datauser:
                    conn.delete_user(user_id=du.user_id)

                    fts = []
                    for f in fingers:
                        if f.uid == du.uid:
                            fts.append(f)

                    conn.save_user_template(du,fts)        


                conn.enable_device()
            except Exception as e:
                messages.error(r,"Proccess terminate : {}".format(e))
            finally:
                if conn:
                    conn.disconnect()



    return redirect("cdatamesin")

@login_required
def cpdivisi(r):
    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        master = r.POST.get("mesin")
        divisi = r.POST.getlist("divisi[]")
        mesin_tujuan = r.POST.getlist("mesint[]")
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=divisi,aktif=1)
        
        datauser = []

        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=master)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()


            datamesin = conn.get_users()
            fingers = []
            for dm in datamesin:
                for pgw in pegawai:
                    if dm.user_id == pgw.userid:
                        datauser.append(dm)
            
            for du in datauser:
                for i in range(1,11):
                    ft = conn.get_user_template(uid=du.uid,temp_id=i)
                    if ft is not None:
                        fingers.append(ft)
            conn.enable_device()
        except Exception as e:
            messages.error(r,"Process terminate : {}".format(e))
        finally:
            if conn:
                conn.disconnect()


        for m in mesin_tujuan:
            try:
                mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=m)
                zk = ZK(mesin_tujuan,4370)
                conn = zk.connect()
                conn.disable_device()
            


                for du in datauser:
                    conn.delete_user(user_id=du.user_id)

                    fts = []
                    for f in fingers:
                        if f.uid == du.uid:
                            fts.append(f)

                    conn.save_user_template(du,fts)        


                conn.enable_device()
            except Exception as e:
                messages.error(r,"Proccess terminate : {}".format(e))
            finally:
                if conn:
                    conn.disconnect()



    return redirect("cdatamesin")

@login_required
def adduser_machine(r): 
    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        mesin = r.POST.get("mesin")
        nama = r.POST.get("nama")
        level = r.POST.get("level")
        userid = r.POST.get("userid")
        password = r.POST.get("password")

        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=mesin)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()

            users = conn.get_users()
            uids = [user.uid for user in users]

            n_data = 1
            last_uid = sorted(uids)[-1]
            uid_ready = [uid for uid in range(uids[0], uids[-1] +1 ) if uid not in uids]
            if len(uid_ready) <= 0:
                uid = last_uid + 1
                if level == 1:
                    conn.set_user(uid=uid,name=nama,password=password,user_id=userid,privilege=const.USER_ADMIN,card=0,group_id='')
                else:
                    conn.set_user(uid=uid,name=nama,password=password,user_id=userid,privilege=const.USER_DEFAULT,card=0,group_id='')
            else:
                uid = uid_ready[0]
                if level == 1:
                    conn.set_user(uid=uid,name=nama,password=password,user_id=userid,privilege=const.USER_ADMIN,card=0,group_id='')
                else:
                    conn.set_user(uid=uid,name=nama,password=password,user_id=userid,privilege=const.USER_DEFAULT,card=0,group_id='')


            conn.enable_device()
        except Exception as e:
            messages.error(r,"Proccess terminate : {}".format(e))
        finally:
            conn.disconnect()
    return redirect("cdatamesin")


@login_required
def edituser_machine(r):
    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        mesin = r.POST.get("mesin")
        pegawai = r.POST.get("pegawai")
        nama = r.POST.get("nama")
        password =r.POST.get("password")
        userid =r.POST.get("userid")
        level =r.POST.get("level")
        

        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=mesin)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()

            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(id=pegawai,aktif=1)
            if not pegawai.exists():
                messages.error(r,'Pegawai tidak ada')
                return redirect("")

            users = conn.get_users()
            user = [user for user in users if user.user_id == pegawai[0].userid]
            
            if level == 0:
                conn.set_user(uid=user[0].uid,name=nama,password=password,user_id=userid,privilege=const.USER_DEFAULT,card=0,group_id='')
            else:
                conn.set_user(uid=user[0].uid,name=nama,password=password,user_id=userid,privilege=const.USER_ADMIN,card=0,group_id='')

            conn.enable_device()

        except Exception as e:
            messages.error(r,"Proccess terminate : {}".format(e))
        finally:
            if conn:
                conn.disconnect()
    return redirect("cdatamesin")   


@login_required
def deleteuser_machine(r):
    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        pegawai = r.POST.getlist("pegawai[]")
        mesin = r.POST.getlist("mesint[]")

        pgw = pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1,id__in=pegawai)
        userids = [ user.userid for user in pgw ]

        for m in mesin:
            try:
                mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=m)
                zk = ZK(mesin.ipaddress,4370)
                conn = zk.connect()
                conn.disable_device()
                for userid in userids:
                    conn.delete_user(user_id=int(userid))
                conn.enable_device()
            except Exception as e:
                messages.error(r,"Proccess terminate : {}".format(e))
            finally:
                if conn:
                    conn.disconnect()
    return redirect("cdatamesin")

@login_required
def deleteuser_machineu(r):
    user = r.user.username

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        pegawai = r.POST.get("userid")
        mesin = r.POST.getlist("mesint[]")

        userids = pegawai.split(",")
        for m in mesin:
            try:
                mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=m)
                zk = ZK(mesin.ipaddress,4370)
                conn = zk.connect()
                conn.disable_device()
                for userid in userids:
                    conn.delete_user(user_id=int(userid))
                conn.enable_device()
            except Exception as e:
                messages.error(r,"Proccess terminate : {}".format(e))
            finally:
                if conn:
                    conn.disconnect()
    return redirect("cdatamesin")


@login_required
def hapusabsen(r,id):

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(id))
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()
            conn.clear_attendance()
            messages.success(r,"Berhasil membersihkan data absensi mesin" + mesin.nama)


            conn.enable_device()
        except Exception as e:
            messages.error(r,e)
        finally:
            if conn:
                conn.disconnect()

    return redirect("amesin")

@login_required
def sesuaikanjam(r,id):

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(id))
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()

            today  = datetime.today()
            conn.set_time(today)
            messages.success(r,"Berhasil sesuaikan jam mesin" + mesin.nama)

            conn.enable_device()
        except Exception as e:
            messages.error(r,e)
        finally:
            if conn:
                conn.disconnect()

    return redirect("amesin")


@login_required
def clearbuffer(r,id):

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    if akses == "admin" or akses == "root":
        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(id))
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()

            conn.free_data()
            messages.success(r,"Berhasil membersihkan buffer mesin" + mesin.nama)

            conn.enable_device()
        except Exception as e:
            messages.error(r,e)
        finally:
            if conn:
                conn.disconnect()

    return redirect("amesin")

@login_required
def tmesin(r):

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    nama = r.POST.get("namamesin")
    ip = r.POST.get("ipaddress")
    status = r.POST.get("status")
    if akses == "admin" or akses == "root":
        if nama == "" or ip == '' or status == '':
            # messages.error(r,"Form tidak boleh kosong")
            return JsonResponse({"status":"error","msg":"Form tidak boleh kosong"},status=400)
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(Q(nama=nama) | Q(ipaddress=ip))
        
        if mesin.exists():
            # messages.error(r,"Mesin sudah ada" + mesin.nama)
            return JsonResponse({"status":"error","msg":"Mesin sudah ada"},status=400)
        mesin_db(
            nama=nama,
            ipaddress=ip,
            status=status
        ).save(using=r.session["ccabang"])
        return JsonResponse({"status":"success","msg":"Berhasil menambahkan mesin"},status=200)
            


@login_required
def hmesin(r):

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    idmesin = r.POST.get("idmesin")
    if akses == "admin" or akses == "root":
        mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(idmesin)).delete()
        # messages.success(r,"Berhasil menghapus mesin")
        return JsonResponse({"status":"success","msg":"Berhasil menghapus mesin"},status=200)
            


@login_required
def emesin(r):

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    nama = r.POST.get("editnamamesin")
    ip = r.POST.get("editipaddress")
    status = r.POST.get("editstatus")
    idmesin = r.POST.get("idmesin")
    if akses == "admin" or akses == "root":
        if nama == '' or ip == '' or status == '' or idmesin == '':
            return JsonResponse({"status":"error","msg":"Form tidak boleh kosong"},status=400)
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(idmesin))
        if not mesin.exists():
            return JsonResponse({"status":"error","msg":"Mesin tidak ada"},status=400)
        checkmesin = mesin_db.objects.using(r.session["ccabang"]).filter(~Q(pk=int(idmesin)),Q(nama=nama) | Q(ipaddress=ip))
        if checkmesin.exists():
            return JsonResponse({"status":"error","msg":"Mesin sudah ada"},status=400)
        mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(idmesin)).update(
            nama=nama,
            ipaddress=ip,
            status=status
        )
        return JsonResponse({"status":"success","msg":"Berhasil edit mesin"},status=200)


@login_required
def getmesin(r):

    iduser = r.user.id
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    idmesin = r.POST.get("idmesin")
    if akses == "admin" or akses == "root":
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(idmesin))
        if not mesin.exists():
            return JsonResponse({"status":"error","msg":"Mesin tidak ada"},status=400)
        data = {
            "nama":mesin[0].nama,
            "ipaddress":mesin[0].ipaddress,
            "status":mesin[0].status
        }

    return JsonResponse({"status":"success","msg":"Berhasil mengambil mesin","data":data},status=200)


@login_required
def listdata(r):
    id_user = r.user.id
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    if akses is not None:
        if akses.akses == "root" or akses.akses == "admin":
            mesin = mesin_db.objects.using(r.session["ccabang"]).all()
            sid = akses.sid_id
            data = {
                "dsid":sid,
                "sid":sid,
                "akses":akses.akses,
                "mesin":mesin
            }
            return render(r,"hrd_app/mesin/listdata.html",data)

        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")
    else:
        messages.error(r,"Akses anda belum ditentukan")
        return redirect("beranda")


@login_required
def listdata_json(r):
    try:
        iduser = r.user.id
        data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
        akses = data_akses.akses 
        mesin = r.POST.get("mesin")
        userid = r.POST.get("userid")
        if mesin is None:
            return JsonResponse({"status":"error","msg":"Silahkan pilih mesin terlebih dahulu"},status=400)
        if akses == "admin" or akses == "root":
            if userid is not None:
                luserid = userid.split(",")
                luserid = [iduser.strip() for iduser in luserid]
            mesin = mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(mesin)).last()
            if mesin is None:
                return JsonResponse({"status":"error","msg":"Mesin tidak ada"},status=400)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()
            users = conn.get_users()
            data = []
            for user in users:
                if userid is not None:
                    if user.user_id in luserid:
                        obj = {
                            "userid":user.user_id,
                            "nama":user.name,
                            "mesin":f"{mesin.ipaddress} - {mesin.nama}"
                        }
                        data.append(obj)
                else:
                    obj = {
                        "userid":user.user_id,
                        "nama":user.name,
                        "mesin":f"{mesin.ipaddress} - {mesin.nama}"
                    }
                    data.append(obj)
            conn.disconnect()
            data = sorted(data,key=lambda i: i["userid"])
        return JsonResponse({"status":"success","msg":"Berhasil mengambil mesin","data":data},status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"status":'error',"msg":"Terjadi kesalahan"},status=400)
# @login_required
# def get_mesin(r,mesin):

#     iduser = r.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses 
#     if akses == "admin" or akses == "root":
#         mesin = mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(mesin))
#         if not mesin.exists():
#             return JsonResponse({"status":"error","msg":"Mesin tidak ada"},status=400)
#         data = {
#             "nama":mesin[0].nama,
#             "ipaddress":mesin[0].ipaddress,
#             "status":mesin[0].status
#         }

#     return JsonResponse({"status":"success","msg":"Berhasil mengambil mesin","data":data},status=200)
            



# -------------------------------------------------------------------------------------------------------------------------------
# Registrasi

# @login_required # Menampilkan data user_id terakhir berdasarkan status pegawai (staff, karyawan, dll)
# def last_userid(request):
    
#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         lid = []
#         status = status_pegawai_db.objects.all().order_by('id')              
        
#         for s in status:
#             pg = pegawai_db.objects.filter(status_id=s.id).order_by('userid').last()
            
#             if pg.userid is not None:    
#                 data_id = {
#                     'status':s.status,
#                     'lid':pg.userid
#                 }
#                 lid.append(data_id)
#             else:                
#                 data_id = {
#                     'status':s.status,
#                     'lid':'Belum ada'
#                 }
#                 lid.append(data_id)
        
#         data = {
#             'status':status,
#             'lid': lid,
#             'akses':akses,
#             'asid':data_akses.sid_id
#         }

#         return render(request, 'hrd_app/last_userid.html', data)

#     else:
#         return redirect('beranda')

# @login_required # Menampilkan daftar mesin finger print untuk dikeluarkan datanya di fungsi data_mesin
# def tarik_data_user(request):
    
#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         data_mesin = mesin_db.objects.using(r.session["ccabang"]).all()

#         data = {
#             'mesin' : data_mesin,
#             'akses':akses,
#             'asid':data_akses.sid_id
#         }

#         return render (request, 'hrd_app/data_mesin.html', data)

#     else:
#         return redirect('beranda')

# # Menampilkan data user di mesin finger yang belum terdapat dalam table datamesin_db
# # Form input pegawai untuk disimpan dalam database
# @login_required       
# def data_mesin(request, ip):
    
#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         # untuk dropdown list
#         data_mesin_all = mesin_db.objects.using(r.session["ccabang"]).all().order_by('nama_mesin')

#         # -------------------------------------------

#         userid = []
#         x = []
#         y = []

#         #conn = None
#         zk = ZK(ip, port=4370, timeout=5)
#         try:

#             conn = zk.connect()
#             conn.disable_device()

#             # kode disini
#             users = conn.get_users()   

#             for u in users:
#                 userid.append(u.user_id)                          

#             conn.enable_device()
#         except Exception as e:
#             messages.error(request, "Process terminate : {}".format(e))
#         finally:
#             if conn:
#                 conn.disconnect()

#         # ------------------------------------------------

#         hitung = datamesin_db.objects.all().count()
        
#         if hitung == 0:            

#             data = {
#                 'mesin' : data_mesin_all,
#                 'ip':ip,
#                 'uids' : userid,
#                 'akses':akses,
#                 'asid':data_akses.sid_id
#             } 

#             return render(request, 'hrd_app/data_mesin_spesifik.html', data)

#         else:
#             data_mesin = datamesin_db.objects.all()            

#             for d in data_mesin:
#                 x.append(d.userid)
#             for user in userid:
#                 y.append(user)

#             userid_2 = [i for i in y if i not in x]

#             data = {
#                 'mesin' : data_mesin_all,
#                 'ip':ip,
#                 'uids' : userid_2,
#                 'akses':akses,
#                 'asid':data_akses.sid_id
#             }

#             return render(request, 'hrd_app/data_mesin_spesifik.html', data)

#         return render(request, 'hrd_app/data_mesin_spesifik.html', {'akses':akses})

#     else:
#         return redirect('beranda')

# @login_required
# def form_tambah_pegawai(request, uid, ip):
    
#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         status = status_pegawai_db.objects.all().order_by('id')
#         divisi = divisi_db.objects.all().order_by('id')
#         data_mesin_all = mesin_db.objects.using(r.session["ccabang"]).all().order_by('nama_mesin')
#         jamkerja = kelompok_kerja_db.objects.all()
#         hari = hari_db.objects.all()
#         counter = counter_db.objects.all().order_by('counter')
#         none_counter = counter_db.objects.get(counter='None')

#         karyawan = jabatan_db.objects.get(jabatan='Karyawan')
#         kid = karyawan.id
#         nama_jabatan = karyawan.jabatan

#         jabatan = jabatan_db.objects.filter(~Q(id=kid)).order_by('id')
        
#         data = {
#             'mesin':data_mesin_all,
#             'status':status,
#             'divisi':divisi,
#             'jam':jamkerja,
#             'userid':uid,
#             'ip': ip,
#             'hari':hari,
#             'counter':counter,
#             'nc_id':none_counter.id,
#             'nc_name':none_counter.counter,
#             'jabatan':jabatan,
#             'kid':kid,
#             'nj':nama_jabatan,
#             'akses':akses,
#             'asid':data_akses.sid_id
#         }

#         return render(request, 'hrd_app/tambah_pegawai.html', data)
#     else:
#         return redirect ('beranda')        

# @login_required # untuk mengarahkan kembali ke fungsi data_mesin setelah proses submit dari fungsi data_mesin
# def redirect_ip(request):
    
#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         mesin = request.POST.get('mesin')

#         data_mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(mesin))
#         ip = data_mesin.ip_address

#         return redirect ('data_mesin', ip=ip)

#     else:
#         return redirect('beranda')
        
# @login_required # Menampilkan daftar mesin yang sudah di simpan dalam database
# def mesin(request):

#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         data_mesin = mesin_db.objects.using(r.session["ccabang"]).all()               

#         data = {
#             'user' : user,
#             'akses':akses,
#             'mesin' : data_mesin,
#             'asid':data_akses.sid_id
#         }

#         return render(request,'hrd_app/mesin.html', data)

#     else:
#         return redirect('beranda') 

# @login_required # Menambah mesin ke dalam table Mesin
# def olah_mesin(request):

#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         id_mesin = request.POST.get('id')
#         nama_mesin = request.POST.get('nama_mesin')
#         ip_address = request.POST.get('ip_address')
#         status = request.POST.get('status')

#         try:
#             if id_mesin is None:

#                 mesin = mesin_db(
#                     nama_mesin=nama_mesin,
#                     ip_address=ip_address,
#                     status=status
#                 )
#                 mesin.save(using=r.session["ccabang"])

#                 messages.success(request, 'Mesin finger berhasil ditambahkan ke dalam database.')

#             else:
#                 mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=id_mesin)
#                 mesin.nama_mesin = nama_mesin
#                 mesin.ip_address = ip_address 
#                 mesin.status = status   
#                 mesin.save(using=r.session["ccabang"])

#                 messages.success(request, 'Mesin finger berhasil diubah.')

#         except IntegrityError:
#             messages.error(request, 'Nama mesin finger atau ip address sudah terdapat di database !')    

#         return redirect('mesin')

#     else:
#         return redirect('beranda')

# @login_required # Hapus mesin di table Mesin
# def hapus_mesin(request):

#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         idm = request.POST.get('id')

#         mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(idm))
#         mesin.delete()

#         messages.success(request, 'Mesin finger berhasil dihapus dari database.')

#         return redirect('mesin')

#     else:
#         return redirect('beranda')

# @login_required # Menghapus data absensi atau enrollment di mesin fingerprint
# def hapus_absensi(request, ip):
    
#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         conn = None
#         zk = ZK(ip, port=4370, timeout=5)
#         try:
#             conn = zk.connect()
#             conn.disable_device()

#             # kode disini
#             conn.clear_attendance()

#             messages.success(request, 'Absensi berhasil dihapus dari mesin finger.')

#             conn.enable_device()
#         except Exception as e:
#             print ("Process terminate : {}".format(e))
#             messages.error(request, 'Process terminate : {}'.format(e))
#         finally:
#             if conn:
#                 conn.disconnect()                  

#         return redirect('mesin')

#     else:
#         return redirect('beranda')

# @login_required # Menyesuaikan jam di mesin dengan jam di pc
# def sesuaikan_jam(request, ip):

#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         conn = None
#         zk = ZK(ip, port=4370, timeout=5)
#         try:
#             conn = zk.connect()
#             conn.disable_device()

#             # kode disini
#             newtime = datetime.today()
#             conn.set_time(newtime)

#             messages.success(request, 'Jam mesin finger berhasil disesuaikan dengan jam perangkat')

#             conn.enable_device()
#         except Exception as e:
#             print ("Process terminate : {}".format(e))
#             messages.error(request, "Process terminate : {}".format(e))
#         finally:
#             if conn:
#                 conn.disconnect()        

#         return redirect('mesin')

#     else:
#         return redirect('beranda')

# @login_required # Clear Buffer mesin finger
# def clear_buffer(request, ip):
    
#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         conn = None
#         zk = ZK(ip, port=4370, timeout=5)
#         try:
#             conn = zk.connect()
#             conn.disable_device()

#             # kode disini
#             conn.free_data()

#             messages.success(request, 'Buffer telah dibersihkan dari mesin finger.')

#             conn.enable_device()
#         except Exception as e:
#             print ("Process terminate : {}".format(e))
#             messages.error(request, "Process terminate : {}".format(e))
#         finally:
#             if conn:
#                 conn.disconnect()        

#         return redirect('mesin')

#     else:
#         return redirect('beranda')

# @login_required # cek koneksi ke mesin finger
# def cek_koneksi(request):
    
#     user = request.user.username

#     iduser = request.user.id
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin' or akses == 'user':

#         hitung = mesin_db.objects.using(r.session["ccabang"]).all().count()
        
#         if hitung < 1:
#             messages.warning(request, 'Anda belum menambahkan mesin finger dalam database, silahkan klik <a href="mesin">"Kelola Mesin"</a> untuk menambahkan Mesin Finger.', extra_tags='safe')
#         else:    
#             mesin = mesin_db.objects.using(r.session["ccabang"]).all()

#             for m in mesin:
#                 ip = m.ip_address
            
#                 conn = None
#                 zk = ZK(ip, port=4370, timeout=60)
#                 try:
#                     conn = zk.connect()
#                     conn.disable_device()

#                     hasil = conn.get_network_params()
                    
#                     fmr = '{}{}{}{}{}{}{}{}'.format('Mesin Finger : ',m.nama_mesin,' - ','Terkoneksi',' - ','( ',m.ip_address,' )')            

#                     messages.info(request, fmr)         

#                     conn.enable_device()
#                 except Exception as e:
#                     fmr2 = '{}{}{}{}{}{}{}{}'.format('Mesin Finger : ',m.nama_mesin,' - ','Gagal Terkoneksi',' - ','( ',m.ip_address,' )')
#                     print ("Process terminate : {}".format(e))
#                     messages.error(request, fmr2)
#                 finally:
#                     if conn:
#                         conn.disconnect()       

#         return render (request, 'hrd_app/cek_koneksi.html',{'akses':akses, 'asid':data_akses.sid_id})

#     else:
#         return redirect('beranda')
# # -------------------------------------------------------------------------------------------
# # Kelola data user di mesin
# @login_required
# def all_copymaster_machine(request):
    
#     master = request.POST.get('master')
#     tujuan = request.POST.getlist('tujuan')

#     mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(master))
#     ip_master = mesin.ip_address
    
#     # ---------------------------------------------------------------------------------------------------------

#     datauser = []
#     user_mesin = []
#     ft = []

#     zk = ZK(ip_master, port=4370)
#     try:

#         conn = zk.connect()
#         conn.disable_device()

#         # ambil data dari master
#         users = conn.get_users()
#         templates = conn.get_templates()

#         # Data user
#         for user in users:
#             datauser.append(user)
        
#         # Data finger template
#         for t in templates:

#             jari = t.json_pack()

#             data = {
#                 'size' : jari['size'],
#                 'uid' : jari['uid'],
#                 'fid' : jari['fid'],
#                 'valid' : jari['valid'],
#                 'template' : t.template,                        
#             }                  

#             ft.append(data)
        
#     except Exception as e:
#         messages.error(request, "Process terminate : {}".format(e))
#     finally:
#         if conn:
#             conn.disconnect() 

#     # ------------------------------------------------------------------------------------
#     # copy data user yang dipilih dari mesin master ke mesin tujuan 
#     mt = mesin_db.objects.using(r.session["ccabang"]).filter(id__in=tujuan)
#     for mesin in mt:
#         ip_tujuan = mesin.ip_address

#         zk = ZK(ip_tujuan, port=4370)
#         try:

#             conn = zk.connect()
#             conn.disable_device()  

#             users = conn.get_users()
#             for u in users:
#                 user_mesin.append(u.user_id)          
                       
#             for user in datauser:

#                 if user.user_id in user_mesin:
#                     pass
#                 else:                
#                     fingers = []
                    
#                     for t in ft:
#                         if user.uid == t['uid']:
                            
#                             size = t['size']
#                             uid = user.uid
#                             fid = t['fid']
#                             valid = t['valid']
#                             template = t['template']                 

#                             jari = Finger(size, uid, fid, valid, template)

#                             pack = jari.json_pack()
#                             unpack = jari.json_unpack(pack)

#                             fingers.append(unpack)

#                     conn.save_user_template(user,fingers)

#             conn.enable_device()
            
#         except Exception as e:
#             print ("Message : {}".format(e))
#         finally:
#             if conn:
#                 conn.disconnect()        
    
#     return redirect('kirim_data')

# @login_required
# def severaluser_copymaster_machine(request):

#     # ambil data user yang dipilih dari mesin master
#     master = request.POST.get('master')
#     tujuan = request.POST.getlist('tujuan')
#     pegawai = request.POST.getlist('pegawai')

#     mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(master))
#     ip_master = mesin.ip_address

#     user_mesin = []
#     datauser = []
#     ft = []    

#     if 'All' in pegawai:
#         userid_list = [item.userid for item in pegawai_db.objects.filter(aktif=1)]
#     else:    
#         userid_list = [item.userid for item in pegawai_db.objects.filter(id__in=pegawai,aktif=1)]
#     # siti anisah
    
#     # master
#     zk = ZK(ip_master, port=4370)
#     try:

#         conn = zk.connect()
#         conn.disable_device()

#         # ambil data dari master
#         users = conn.get_users()
#         # templates = conn.get_templates()

#         # Data user
#         for user in users:
#             for ul in userid_list:
#                 if user.user_id == ul:
#                     datauser.append(user)
        
#         # Data finger template
#         for du in datauser:
#             t = conn.get_user_template(uid=du.uid) 
#             if t is not None:

#                 jari = t.json_pack()

#                 data = {
#                     'size' : jari['size'],
#                     'uid' : jari['uid'],
#                     'fid' : jari['fid'],
#                     'valid' : jari['valid'],
#                     'template' : t.template,                        
#                 }                  

#                 ft.append(data) 
#             else:
#                 pass              

#         conn.enable_device()
        
#     except Exception as e:
#         messages.error(request, "Process terminate : {}".format(e))
#     finally:
#         if conn:
#             conn.disconnect()
    
#     # ------------------------------------------------------------------------------------
#     # copy data user yang dipilih dari mesin master ke mesin tujuan 
#     mt = mesin_db.objects.using(r.session["ccabang"]).filter(id__in=tujuan)
#     for mesin in mt:
#         ip_tujuan = mesin.ip_address

#         zk = ZK(ip_tujuan, port=4370)
#         try:

#             conn = zk.connect()
#             conn.disable_device() 

#             users = conn.get_users()
#             for u in users:
#                 if u.user_id in userid_list:
#                     user_mesin.append(u.user_id)                       
                     
#             for user in datauser: 

#                 conn.delete_user(user_id=user.uid)

#                 fingers = []
#                 for t in ft:
#                     if user.uid == t['uid']:
                        
#                         size = t['size']
#                         uid = user.uid
#                         fid = t['fid']
#                         valid = t['valid']
#                         template = t['template']                 

#                         jari = Finger(size, uid, fid, valid, template)

#                         pack = jari.json_pack()
#                         unpack = jari.json_unpack(pack)

#                         fingers.append(unpack)

#                 conn.save_user_template(user,fingers)
                    

#             conn.enable_device()
            
#         except Exception as e:
#             messages.error(request, "Process terminate : {}".format(e))
#         finally:
#             if conn:
#                 conn.disconnect()    

#     return redirect('kirim_data')

# @login_required
# def severaldiv_copymaster_machine(request):

#     # ambil data user yang dipilih dari mesin master
#     master = request.POST.get('master')
#     tujuan = request.POST.getlist('tujuan')
#     divisi = request.POST.getlist('divisi')

#     mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(master))
#     ip_master = mesin.ip_address
   
#     user_mesin = []
#     datauser = [] 
#     ft = []

#     if 'All' in divisi:
#         userid_list = [item.userid for item in pegawai_db.objects.filter(aktif=1)]
#     else:    
#         userid_list = [item.userid for item in pegawai_db.objects.filter(divisi_id__in=divisi, aktif=1)]
    
#     zk = ZK(ip_master, port=4370)
#     try:

#         conn = zk.connect()
#         conn.disable_device()

#         # ambil data dari master
#         users = conn.get_users()
#         # templates = conn.get_templates()

#         # Data user
#         for user in users:
#             for ul in userid_list:
#                 if user.user_id == ul:
#                     datauser.append(user)
        
#         # Data finger template
#         for du in datauser:
#             t = conn.get_user_template(uid=du.uid)
            
#             if t is not None:

#                 jari = t.json_pack()

#                 data = {
#                     'size' : jari['size'],
#                     'uid' : jari['uid'],
#                     'fid' : jari['fid'],
#                     'valid' : jari['valid'],
#                     'template' : t.template,                        
#                 }                  

#                 ft.append(data)
#             else:
#                 pass    

#         conn.enable_device()
        
#     except Exception as e:
#         messages.error(request, "Process terminate : {}".format(e))
#     finally:
#         if conn:
#             conn.disconnect()      
    
#     # ------------------------------------------------------------------------------------
#     # copy data user yang dipilih dari mesin master ke mesin tujuan 
#     mt = mesin_db.objects.using(r.session["ccabang"]).filter(id__in=tujuan)
#     for mesin in mt:
#         ip_tujuan = mesin.ip_address

#         # simpan data user
#         zk = ZK(ip_tujuan, port=4370)
#         try:

#             conn = zk.connect()
#             conn.disable_device() 

#             users = conn.get_users()
#             for u in users:
#                 if u.user_id in userid_list:
#                     user_mesin.append(u.user_id)           
                        
#             for user in datauser:
#                 if user.user_id in user_mesin:
#                     pass
#                 else:                
#                     fingers = []
                    
#                     for t in ft:
#                         if user.uid == t['uid']:
                            
#                             size = t['size']
#                             uid = user.uid
#                             fid = t['fid']
#                             valid = t['valid']
#                             template = t['template']                 

#                             jari = Finger(size, uid, fid, valid, template)

#                             pack = jari.json_pack()
#                             unpack = jari.json_unpack(pack)

#                             fingers.append(unpack)

#                     conn.save_user_template(user,fingers)
            
#             conn.enable_device()
            
#         except Exception as e:
#             messages.error(request, "Process terminate : {}".format(e))
#         finally:
#             if conn:
#                 conn.disconnect()        
    
#     return redirect('kirim_data')

# @login_required
# def adduser_machine(request):

#     mesin = request.POST.get('mesin')
#     nama = request.POST.get('nama')
#     password = request.POST.get('password')
#     userid = request.POST.get('userid')
#     level = request.POST.get('level')

#     mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(mesin))
#     ip_mesin = mesin.ip_address   

#     # tambah data user 
#     zk = ZK(ip_mesin, port=4370)
#     try:

#         conn = zk.connect()
#         conn.disable_device()            

#         users = conn.get_users()

#         # uid yang tersedia di mesin
#         uid_range = [user.uid for user in users]  

#         n_data = 1            
#         last_uid = sorted(uid_range)[-1]
#         uid_ready = [item for item in range(uid_range[0], uid_range[-1]+1) if item not in uid_range]   
        
#         if not uid_ready:
#             uid_use = last_uid + 1

#             # simpan data user di mesin tujuan    
#             if level == 'admin': 
#                 conn.set_user(uid=uid_use, name=nama, privilege=const.USER_ADMIN, password=password, group_id='', user_id=userid, card=0)
#             else:
#                 conn.set_user(uid=uid_use, name=nama, privilege=const.USER_DEFAULT, password=password, group_id='', user_id=userid, card=0)
#         else:
#             uid_use = [item for item in uid_ready[0:n_data]] 

#             # simpan data user di mesin tujuan    
#             if level == 'admin': 
#                 conn.set_user(uid=uid_use[0], name=nama, privilege=const.USER_ADMIN, password=password, group_id='', user_id=userid, card=0)
#             else:
#                 conn.set_user(uid=uid_use[0], name=nama, privilege=const.USER_DEFAULT, password=password, group_id='', user_id=userid, card=0)
                   

#         conn.enable_device()
        
#     except Exception as e:
#         messages.error(request, "Process terminate : {}".format(e))
#     finally:
#         if conn:
#             conn.disconnect()    

#     return redirect('kirim_data')

# @login_required
# def edituser_machine(request):

#     mesin = request.POST.get('mesin')
#     pegawai = request.POST.get('pegawai')
#     nama = request.POST.get('nama')
#     password = request.POST.get('password')
#     userid = request.POST.get('userid')
#     level = request.POST.get('level')

#     mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(mesin))
#     ip_mesin = mesin.ip_address   

#     pg = pegawai_db.objects.get(id=int(pegawai))
#     userid_pegawai = pg.userid


#     # edit user 
#     zk = ZK(ip_mesin, port=4370)
#     try:

#         conn = zk.connect()
#         conn.disable_device() 

#         users = conn.get_users()
#         for u in users:
#             if u.user_id == userid_pegawai:         

#                 # simpan data user di mesin tujuan    
#                 if level == 'admin': 
#                     conn.set_user(uid=u.uid, name=nama, privilege=const.USER_ADMIN, password=password, group_id='', user_id=userid, card=0)
#                 else:
#                     conn.set_user(uid=u.uid, name=nama, privilege=const.USER_DEFAULT, password=password, group_id='', user_id=userid, card=0)    

#         conn.enable_device()
        
#     except Exception as e:
#         messages.error(request, "Process terminate : {}".format(e))
#     finally:
#         if conn:
#             conn.disconnect()    

#     return redirect('kirim_data')

# @login_required
# def deleteusername_machine(request):

#     pegawai = request.POST.getlist('nama')
#     dmesin = request.POST.getlist('mesin')

#     userid_list = [item.userid for item in pegawai_db.objects.filter(id__in=pegawai)]   
    
#     if 'All' in dmesin:
#         mesin = mesin_db.objects.using(r.session["ccabang"]).all()
#     else:
#         mesin = mesin_db.objects.using(r.session["ccabang"]).filter(id__in=dmesin)

#     for m in mesin:
#         ip_mesin = m.ip_address

#         # delete user 
#         zk = ZK(ip_mesin, port=4370)
#         try:

#             conn = zk.connect()
#             conn.disable_device()            

#             for userid in userid_list:
#                 conn.delete_user(user_id=userid)

#             conn.enable_device()
            
#         except Exception as e:
#             messages.error(request, "Process terminate : {}".format(e))
#         finally:
#             if conn:
#                 conn.disconnect()    

#     return redirect('kirim_data')

# @login_required
# def deleteuserid_machine(request):

#     duserid = request.POST.get('userid')
#     dmesin = request.POST.getlist('mesin')

#     ulist = duserid.split(',')

#     if 'All' in dmesin:
#         mesin = mesin_db.objects.using(r.session["ccabang"]).all()
#     else:
#         mesin = mesin_db.objects.using(r.session["ccabang"]).filter(id__in=dmesin)

#     for m in mesin:
#         ip_mesin = m.ip_address

#         # delete user 
#         zk = ZK(ip_mesin, port=4370)
#         try:

#             conn = zk.connect()
#             conn.disable_device()            

#             for userid in ulist:
#                 conn.delete_user(user_id=int(userid))

#             conn.enable_device()
            
#         except Exception as e:
#             messages.error(request, "Process terminate : {}".format(e))
#         finally:
#             if conn:
#                 conn.disconnect()    

#     return redirect('kirim_data')