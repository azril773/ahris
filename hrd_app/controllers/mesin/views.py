from hrd_app.controllers.lib import *
from zk import user as usr,finger


def amesin(r):
    iduser = r.session["user"]["id"]
        
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
            "nama":r.session["user"]["nama"],
            'modul_aktif' : 'Counter'     
        }
        
        return render(r,'hrd_app/mesin/mesin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    

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
    


def admesin(r,id): 
    iduser = r.session["user"]["id"]
        
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
                conn.disconnect()
            except Exception as e:
                messages.error(r,"Proccess terminate: {}".format(e))


        data = {       
            'dsid': dsid,
            "mesin":mesin,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'id':id,
            'userid':userid,
            'modul_aktif' : 'Counter'
        }

        
        
        return render(r,'hrd_app/mesin/dmesin.html',data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')



def rmesin(r,userid,id,uid):
    iduser = r.session["user"]["id"]

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
            "nama":r.session["user"]["nama"],
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




def tambah_data_pegawai(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        user = akses_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])
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
                conn.disconnect()

        except Exception as e:
            return JsonResponse({"status":"error","msg":e},status=500)
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
                add_by=r.session["user"]["nama"],
                edit_by=r.session["user"]["nama"]

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
            user = r.session["user"]["nama"]

            
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)





def datamesin(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'id':id,
            'modul_aktif' : 'Counter'
        }
        
        
        return render(r,'hrd_app/mesin/datamesin.html',data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


def add_data(r,id):
    user = r.session["user"]["nama"]

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses   
    try:
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(id=int(id))
        conn = ZK(mesin[0].ipaddress,port=4370)
        conn.connect()
        conn.disable_device()


        users = conn.get_users()


        datamesin = [i.userid for i in datamesin_db.objects.using(r.session["ccabang"]).all()]
        userids = [user.user_id for user in users if user.user_id not in datamesin]
        user = [user for user in users]
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(userid__in=userids)
        pegawaiarsip = pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(userid__in=userids)
        templates = conn.get_templates()
        print(pegawaiarsip)
        # pegawai_arsip = pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(userid__in=userids)
        # pegawai = [pgw for pgw in pegawai if pgw.userid in userids]
        # 
        mesin = []
        tmps = []
        for u in user:
            pass
            # pgw = next((p for p in pegawai if p.userid == u.user_id),None)
            # pgwa = next((pg for pg in pegawaiarsip if pg.userid == u.user_id),None)
            # if pgw is not None:
            #     pgw = pgw
            # elif pgwa is not None:
            #     pgw = pgwa
            # else:
            #     # print(f"Data pegawai dengan userid {u.user_id} tidak ada")
            #     continue
            # if u.privilege == const.USER_ADMIN:
            #     level = 14
            # else:
            #     level = 0
            # if u.user_id not in datamesin:
            #     mesin.append(datamesin_db(
            #         uid=u.uid,
            #         nama=pgw.nama,
            #         userid=u.user_id,
            #         level=level,
            #         password=u.password
            #     ))
                
            #     template = [tm for tm in templates if tm.uid == u.uid]
            #     for t in template:
            #         tmps.append(sidikjari_db(
            #             uid=t.uid,
            #             nama=pgw.nama,
            #             userid=u.user_id,
            #             size=t.size,
            #             fid=t.fid,
            #             valid=t.valid,
            #             template=t.template
            #         ))
            # else:
            #     # dm = datamesin_db.objects.using(r.session["ccabang"]).filter(userid=u.user_id).last()
            #     # if not dm:
            #     #     continue
            #     # dm.uid = u.uid
            #     # dm.nama = pgw.nama
            #     # dm.userid = u.user_id
            #     # dm.level = u.level
            #     # dm.password = u.password
            #     # dm.save(using=r.session["ccabang"])
            #     pass


        conn.enable_device()
        conn.disconnect()
        print(mesin)
        print(tmps)
        datamesin_db.objects.using(r.session['ccabang']).bulk_create(mesin)
        sidikjari_db.objects.using(r.session["ccabang"]).bulk_create(tmps)
    except Exception as e:
        messages.error(r, "Process terminate : {}".format(e))
    return redirect("amesin")



def cdatamesin(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        mesin = mesin_db.objects.using(r.session["ccabang"]).all()
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
        divisi = divisi_db.objects.using(r.session["ccabang"]).all()
        datamesin = datamesin_db.objects.using(r.session["ccabang"]).all()
        print(r.session["user"])
        data = {       
            'dsid': dsid,
            "mesin":mesin,
            "pegawai":pegawai,
            "datamesin":datamesin,
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            "divisi":divisi,
            "admin":r.session["user"]["admin"],
            'modul_aktif' : 'Mesin'     
        }
        
        return render(r,'hrd_app/mesin/cdatamesin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@authorization(["root","it"])
def cekmesin(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        disc = []
        for m in mesin_db.objects.using(r.session["ccabang"]).filter(status="Active"):
            try:
                zk = ZK(m.ipaddress,4370,60)
                conn = zk.connect()
                if not conn.is_connect:
                    disc.append({"ipaddress":m.ipaddress,"nama":m.nama,"id":m.pk})
            except:
                disc.append({"ipaddress":m.ipaddress,"nama":m.nama,"id":m.pk})
                
        return JsonResponse({"status":"success","msg":"Berhasil cek semua mesin","data":disc},status=200)
    else:    
        return JsonResponse({"status":"error","msg":"Terjadi kesalahan"},status=400)


@authorization(["root","it"])
def cpalldata(r):
    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
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
        fingers = conn.get_templates()
        for dm in datamesin:
            for pgw in pegawai:
                if dm.user_id == pgw.userid:
                    datauser.append(dm)
        
        conn.enable_device()
        conn.disconnect()
    except Exception as e:
        messages.error(r,"Process terminate : {}".format(e))
    
    for m in mesin_tujuan:
        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=m)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()
            for du in datauser:
                conn.set_user(du.uid,du.name,du.privilege,du.password,du.group_id,du.user_id,du.card)
                fts = []
                fgr = [f for f in fingers if f.uid == du.uid]
                print(du)
                print(fgr)
                conn.save_user_template(du,fgr)       
            conn.enable_device()
            conn.disconnect()
        except Exception as e:
            messages.error(r,"Proccess terminate : {}".format(e))

    return redirect("cdatamesin")

@authorization(["root","it"])
def cppegawai(r):
    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    master = r.POST.get("mesin")
    pegawai = r.POST.getlist("pegawai[]")
    mesin_tujuan = r.POST.getlist("mesint[]")
    if len(pegawai) <= 0:
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
    else:
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=pegawai)
    print(pegawai)
    datauser = []
    try:
        mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=master)
        zk = ZK(mesin.ipaddress,4370)
        conn = zk.connect()
        conn.disable_device()
        datamesin = conn.get_users()
        fingers = conn.get_templates()
        for dm in datamesin:
            for pgw in pegawai:
                if dm.user_id == pgw.userid:
                    datauser.append(dm)
        
        conn.enable_device()
        conn.disconnect()
    except Exception as e:
        messages.error(r,"Process terminate : {} asal".format(e))
    for m in mesin_tujuan:
        try:
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=m)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()
            for du in datauser:
                conn.set_user(du.uid,du.name,du.privilege,du.password,du.group_id,du.user_id,du.card)
                fts = []
                fgr = [f for f in fingers if f.uid == du.uid]
                print(du)
                print(fgr)
                conn.save_user_template(du,fgr)    
            conn.enable_device()
            conn.disconnect()
        except Exception as e:
            messages.error(r,"Proccess terminate : {} tujuan".format(e))



    return redirect("cdatamesin")

@authorization(["root","it"])
def cpdivisi(r):
    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
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
        fingers = conn.get_templates()
        for dm in datamesin:
            for pgw in pegawai:
                if dm.user_id == pgw.userid:
                    datauser.append(dm)
        
        conn.enable_device()
        conn.disconnect()
    except Exception as e:
        messages.error(r,"Process terminate : {} master".format(e))
    for m in mesin_tujuan:
        try:
            print(datauser)
            mesin = mesin_db.objects.using(r.session["ccabang"]).get(ipaddress=m)
            zk = ZK(mesin.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()
        
            for du in datauser:
                conn.set_user(du.uid,du.name,du.privilege,du.password,du.group_id,du.user_id,du.card)
                fts = []
                fgr = [f for f in fingers if f.uid == du.uid]
                print(fgr)
                conn.save_user_template(du,fgr)        
            conn.enable_device()
            conn.disconnect()
        except Exception as e:
            messages.error(r,"Proccess terminate : {} tujuan".format(e))



    return redirect("cdatamesin")

@authorization(["root","it"])
def adduser_machine(r): 
    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
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
        conn.disconnect()
    except Exception as e:
        messages.error(r,"Proccess terminate : {}".format(e))
    return redirect("cdatamesin")


@authorization(["root","it"])
def edituser_machine(r):
    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
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
        conn.disconnect()
    except Exception as e:
        messages.error(r,"Proccess terminate : {}".format(e))
    return redirect("cdatamesin")   


@authorization(["root","it"])
def deleteuser_machine(r):
    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
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
            conn.disconnect()
        except Exception as e:
            messages.error(r,"Proccess terminate : {}".format(e))
    return redirect("cdatamesin")

@authorization(["root","it"])
def deleteuser_machineu(r):
    user = r.session["user"]["nama"]

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
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
            conn.disconnect()
        except Exception as e:
            messages.error(r,"Proccess terminate : {}".format(e))
    return redirect("cdatamesin")


@authorization(["root","it"])
def hapusabsen(r,id):

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    try:
        mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(id))
        zk = ZK(mesin.ipaddress,4370)
        conn = zk.connect()
        conn.disable_device()
        conn.clear_attendance()
        messages.success(r,"Berhasil membersihkan data absensi mesin" + mesin.nama)
        conn.enable_device()
        conn.disconnect()
    except Exception as e:
        messages.error(r,e)

    return redirect("amesin")

@authorization(["root","it"])
def sesuaikanjam(r,id):

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    try:
        mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(id))
        zk = ZK(mesin.ipaddress,4370)
        conn = zk.connect()
        conn.disable_device()
        today  = datetime.today()
        conn.set_time(today)
        messages.success(r,"Berhasil sesuaikan jam mesin" + mesin.nama)
        conn.enable_device()
        conn.disconnect()
    except Exception as e:
        messages.error(r,e)

    return redirect("amesin")


@authorization(["root","it"])
def clearbuffer(r,id):

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    try:
        mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(id))
        zk = ZK(mesin.ipaddress,4370)
        conn = zk.connect()
        conn.disable_device()
        conn.free_data()
        messages.success(r,"Berhasil membersihkan buffer mesin" + mesin.nama)
        conn.enable_device()
        conn.disconnect()
    except Exception as e:
        messages.error(r,e)

    return redirect("amesin")

@authorization(["root","it"])
def tmesin(r):

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    nama = r.POST.get("namamesin")
    ip = r.POST.get("ipaddress")
    status = r.POST.get("status")
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
            


@authorization(["root","it"])
def hmesin(r):

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    idmesin = r.POST.get("idmesin")
    mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(idmesin)).delete()
    # messages.success(r,"Berhasil menghapus mesin")
    return JsonResponse({"status":"success","msg":"Berhasil menghapus mesin"},status=200)
            


@authorization(["root","it"])
def emesin(r):

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    nama = r.POST.get("editnamamesin")
    ip = r.POST.get("editipaddress")
    status = r.POST.get("editstatus")
    idmesin = r.POST.get("idmesin")
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


@authorization(["root","it"])
def getmesin(r):

    iduser = r.session["user"]["id"]
    data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
    akses = data_akses.akses 
    idmesin = r.POST.get("idmesin")
    mesin = mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(idmesin))
    if not mesin.exists():
        return JsonResponse({"status":"error","msg":"Mesin tidak ada"},status=400)
    data = {
        "nama":mesin[0].nama,
        "ipaddress":mesin[0].ipaddress,
        "status":mesin[0].status
    }
    return JsonResponse({"status":"success","msg":"Berhasil mengambil mesin","data":data},status=200)


@authorization(["root","it"])
def listdata(r):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    mesin = mesin_db.objects.using(r.session["ccabang"]).all()
    sid = akses.sid_id
    data = {
        "dsid":sid,
        "sid":sid,
        "akses":akses.akses,
        "nama":r.session["user"]["nama"],
        "mesin":mesin
    }
    return render(r,"hrd_app/mesin/listdata.html",data)


def testmesin(r):
    pass
    # for pg in pegawai_db.objects.using(r.session["ccabang"]).all():
    #     dm = datamesin_db.objects.using(r.session["ccabang"]).filter(userid=pg.userid).last()
    #     if not dm:
    #         continue

    #     sidikjari = sidikjari_db.objects.using(r.session["ccabang"]).filter(userid=dm.userid)
    #     fingers = []
    #     for ft in sidikjari:
    #         fingers.append(finger.Finger(ft.uid,ft.fid,ft.valid,ft.template))
    
    zk = ZK("15.59.254.214")
    conn = zk.connect()
    conn.disable_device()
    # print(conn.get_users()[-1])
    # conn.delete_user(user_id='99999')
    conn.set_user(name='hahsdy',privilege=const.USER_DEFAULT,password= '',user_id='99995',card=0)
    # conn.sa
    #     user = usr.User(dm.uid,pg.nama,dm.level,dm.password,'',dm.userid,0)
    #     conn.save_user_template(user,fingers)
    conn.enable_device()
    conn.disconnect()

def sinkrondatamemsin(r):
    mesin = mesin_db.objects.using(r.session["ccabang"]).filter(~Q(ipaddress="15.59.254.211"),status="Active")
    userid = [p["userid"] for p in pegawai_db.objects.using(r.session["ccabang"]).all().values("id","userid","nama")]
    useridarsip = [p["userid"] for p in pegawai_db_arsip.objects.using(r.session['ccabang']).all().values("id","userid","nama")]
    userids = userid + useridarsip


    zkmaster = ZK("15.59.254.28323876",4370)
    conn = zkmaster.connect()
    zkmaster.disable_device()
    usersmaster = conn.get_users()
    # usermasters  = [ud.user_id for ud in usersmaster]

    useridac = [us.user_id for us in usersmaster if us.user_id in userids]
    data = {'userid':[],"nama":[],"mesin":''}
    print("OKOKOK")
    useridss = []
    userdata = []
    
    for m in mesin:
        print(m.nama)
        try:
            zk = ZK(m.ipaddress,4370)
            conn2 = zk.connect()
            users = conn2.get_users()
            templates = conn2.get_templates()
            userid = [us for us in users if us.user_id not in useridac]
            for us in userid:
                if us.user_id in userids:
                    if us.user_id not in useridss:
                        conn.set_user(name=us.name,privilege=us.privilege,password=us.password,user_id=us.user_id,card=0)
                        lastuser = conn.get_users()[-1]
                        template = [tmp for tmp in templates if tmp.uid == us.uid]
                        for t in template:
                            user = usr.User(uid=lastuser.uid,name=lastuser.name,privilege=lastuser.privilege,password=lastuser.password,group_id=lastuser.group_id,user_id=lastuser.user_id,card=0)
                            f = finger.Finger(lastuser.uid,t.fid,t.valid,t.template)
                            conn.save_user_template(user,f)


                        useridss.append(us.user_id)
                        # else:
                        #     conn.set_user(uid=,name=us.name,privilege=us.privilege,password=us.password,group_id=us.group_id,user_id=us.user_id,card=0)
            print(useridss)
            # time.sleep(1)
            conn2.enable_device()
            conn2.disconnect()
            # time.sleep(1)
        except:
            conn2.enable_device()
            conn2.disconnect()
    conn.enable_device()
    conn.disconnect()

    # dt = pd.DataFrame(data)
    # dt.to_excel('excel.xlsx')
    return JsonResponse(data,safe=False)


def setuserid(r,sid):
    # Pegawai dan pegawai arsip ada di dalam datamesin
    # Pegawai dengan userid yang ada di dalam datamesin bisa di proses dan bisa mempunyai userid yang baru
    # 
    with transaction.atomic(using=r.session["ccabang"]):
        try:
            if not status_pegawai_db.objects.using(r.session["ccabang"]).filter(pk=sid).last():
                return JsonResponse({"status":'error',"msg":"status pegawai tidak ada"})
            init = 218000
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(status_id=sid).values("id","userid","nama").order_by("nama")
            datamesin = datamesin_db.objects.using(r.session["ccabang"]).all().values("id","nama","userid","uid")
            sidik = sidikjari_db.objects.using(r.session["ccabang"]).all().values("id","userid","uid")
            newdm = []
            newsdk = []
            useridmesin  = [dm["userid"] for dm in datamesin if re.search('218\d{3}',dm["userid"])]
            print(useridmesin)
            newpgw = [pg for pg in pegawai if pg["userid"] not in useridmesin]
            userint = [int(us) for us in useridmesin]
            print(newpgw)
            for pgw in newpgw:
                init += 1
                while True:
                    # print(init)
                    if init in userint:
                        init +=1 
                    else:
                        break
                dtmesin = next((dm for dm in datamesin if dm["userid"] == pgw["userid"]),None)
                if not dtmesin:
                    continue
                sidikjari = [sdk for sdk in sidik if sdk["userid"] == pgw["userid"]]
                    
                pgw["userid"] = init

                for s in sidikjari:
                    s["userid"] = pgw["userid"]
                    newsdk.append(s)
                dtmesin["userid"] = pgw["userid"]
                newdm.append(dtmesin)
            print(pegawai)
            print(newdm)
            print(newsdk)
            pegawai_db.objects.using(r.session["ccabang"]).bulk_update([pegawai_db(id=f["id"],userid=f["userid"]) for f in pegawai],["userid"])
            datamesin_db.objects.using(r.session["ccabang"]).bulk_update([datamesin_db(id=dt["id"],userid=dt["userid"]) for dt in newdm],["userid"])
            sidikjari_db.objects.using(r.session["ccabang"]).bulk_update([sidikjari_db(id=s["id"],userid=s["userid"]) for s in newsdk],["userid"])
        except Exception as e:
            transaction.set_rollback(True,using=r.session["ccabang"])
            print("MASUKKK ERRROR")
            raise e
        

def auto(r):
    pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(status_id=10)
    pgws = pegawai_db.objects.using(r.session["ccabang"]).all()
    id = 1
    for p in pegawai:
        print(id)
        if next((pg for pg in pgws if str(pg.userid) == str(id)), None) is None:
            p.userid = id
            p.save(using=r.session["ccabang"])
            id += 1
        else:
            id += 1
            continue


def sin(r): 
    pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(status_id=10)
    zk = ZK("15.59.254.211",4370)
    conn = zk.connect()
    conn.disable_device()
    users = conn.get_users()
    newpgw = []
    for p in pegawai:
        us = next((user for user in users if user.name.strip() == p.nama.strip() and re.search('217\d{3}',user.user_id.strip()) is not None), None)
        if not us:
            continue

        # newpgw.append(pegawai_db(id=p.pk,userid=us.user_id))
        newpgw.append({
            "id":p.pk,
            'userid':us.user_id,
            'nama':p.nama
        })
    print(len(newpgw))
    print(newpgw,"PLPLPL\n\n\n")
    conn.enable_device()
    conn.disconnect()
    pegawai_db.objects.using(r.session["ccabang"]).bulk_update([pegawai_db(id=pg["id"],userid=pg["userid"]) for pg in newpgw],["userid"])


authorization(["root"])
def byfilter(r):
    if r.method == "POST":
        mesin = r.POST.getlist("mesin[]")
        data = r.POST.get("data")
        filter = r.POST.get("filter")
        print(mesin,data,filter)
        if data is None or mesin is None or filter is None:
            return JsonResponse({"status":'error',"msg":"Harap isi form dengan benar"},status=400)
        mesindb = mesin_db.objects.using(r.session["ccabang"]).filter(id__in=mesin)
        userdt = []
        templatesdt =[]
        for m in mesindb:
            zk = ZK(m.ipaddress,4370)
            conn = zk.connect()
            conn.disable_device()
            users = conn.get_users()
            templates = conn.get_templates()
            user = []
            # Check filter
            if filter == 'nama':
                user = [{"nama":user.name,'uid':user.uid,"userid":user.user_id,'level':user.privilege,"password":user.password,"mesin":m.nama} for user in users if user.name.strip() == data.strip()]
            elif filter == 'userid':
                user = [{"nama":user.name,'uid':user.uid,"userid":user.user_id,'level':user.privilege,"password":user.password,"mesin":m.nama} for user in users if str(user.user_id) == str(data)]
            elif filter == 'uid':
                user = [{"nama":user.name,'uid':user.uid,"userid":user.user_id,'level':user.privilege,"password":user.password,"mesin":m.nama} for user in users if int(user.uid) == int(data)]
            else:
                return JsonResponse({"status":'error',"msg":"Filter tidak diketahui"},status=400)
            
            # Get template by uid user
            if len(user) > 0:
                [templatesdt.append({'uid':tmp.uid,"fid":tmp.fid,"size":tmp.size,"mesin":m.nama}) for tmp in templates if tmp.uid == user[-1]["uid"]]
                userdt.append(user[-1])

            # Enable device and disconnect
            conn.enable_device()
            conn.disconnect()

        return JsonResponse({"status":"success","msg":"berhasil ambil data","users":userdt,"fingers":templatesdt},status=200)

authorization(["root"])
def adddtmesin(r):
    mesin = r.POST.getlist("mesin[]")
    userid = r.POST.getlist("userid[]")
    datamesin = datamesin_db.objects.using(r.session["ccabang"]).filter(userid__in=userid)
    sidikjari = sidikjari_db.objects.using(r.session["ccabang"]).filter(userid__in=userid)
    for m in mesin:
        zk = ZK(m,4370)
        conn = zk.connect()
        conn.disable_device()
        for u in datamesin:
            fingers = [sd for sd in sidikjari if str(sd.userid) == str(u.userid)]
            conn.set_user(uid=u.uid,user_id=u.userid,name=u.nama,password=u.password,privilege=u.level,card=0)
            user = usr.User(uid=u.uid,name=u.nama,privilege=u.level,password=u.password,user_id=u.userid)
            templates = []
            for s in fingers:
                templates.append(finger.Finger(uid=s.uid,fid=s.fid,valid=s.valid,template=s.template))
            conn.save_user_template(user,templates)
        conn.enable_device()
        conn.disconnect()


def senddata(r,sid):
    if sid == 0:
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
    else:
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(status_id=sid)
        
    zk = ZK('15.59.254.212',4370)
    print('ok')
    conn = zk.connect()
    conn.disable_device()
    datamesin = datamesin_db.objects.using(r.session["ccabang"]).all()
    templates = sidikjari_db.objects.using(r.session['ccabang']).all()
    for pgw in pegawai:
        print(pgw)
        dmesin = next((mesin for mesin in datamesin if mesin.userid == pgw.userid), None)
        temp = [sd for sd in templates if sd.userid == pgw.userid]
        if not dmesin:
            continue
        conn.set_user(uid=dmesin.uid,name=dmesin.nama,password=dmesin.password if dmesin.password is not None else '',user_id=dmesin.userid,privilege=dmesin.level)
        user = usr.User(dmesin.uid,name=dmesin.nama,privilege=dmesin.level,password=dmesin.password,user_id=dmesin.userid)
        tmps = []
        print(temp)
        for tmp in temp:
            tmps.append(finger.Finger(uid=tmp.uid,fid=tmp.fid,valid=tmp.valid,template=tmp.template))
        conn.save_user_template(user,tmps)
    conn.enable_device()
    conn.disconnect()





@authorization(["root","it"])
def listdata_json(r):
    try:
        iduser = r.session["user"]["id"]
        data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
        akses = data_akses.akses 
        mesin = r.POST.get("mesin")
        userid = r.POST.get("userid")
        if mesin is None:
            return JsonResponse({"status":"error","msg":"Silahkan pilih mesin terlebih dahulu"},status=400)
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
# 
# def get_mesin(r,mesin):

#     iduser = r.session["user"]["id"]
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses 
#     if akses == "admin" or akses == "root":get_users
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

#  # Menampilkan data user_id terakhir berdasarkan status pegawai (staff, karyawan, dll)
# def last_userid(request):
    
#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

#  # Menampilkan daftar mesin finger print untuk dikeluarkan datanya di fungsi data_mesin
# def tarik_data_user(request):
    
#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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
#        
# def data_mesin(request, ip):
    
#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

# 
# def form_tambah_pegawai(request, uid, ip):
    
#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

#  # untuk mengarahkan kembali ke fungsi data_mesin setelah proses submit dari fungsi data_mesin
# def redirect_ip(request):
    
#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
#     data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
#     akses = data_akses.akses        

#     if akses == 'root' or akses == 'it' or akses == 'admin':

#         mesin = request.POST.get('mesin')

#         data_mesin = mesin_db.objects.using(r.session["ccabang"]).get(id=int(mesin))
#         ip = data_mesin.ip_address

#         return redirect ('data_mesin', ip=ip)

#     else:
#         return redirect('beranda')
        
#  # Menampilkan daftar mesin yang sudah di simpan dalam database
# def mesin(request):

#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

#  # Menambah mesin ke dalam table Mesin
# def olah_mesin(request):

#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

#  # Hapus mesin di table Mesin
# def hapus_mesin(request):

#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

#  # Menghapus data absensi atau enrollment di mesin fingerprint
# def hapus_absensi(request, ip):
    
#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

#  # Menyesuaikan jam di mesin dengan jam di pc
# def sesuaikan_jam(request, ip):

#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

#  # Clear Buffer mesin finger
# def clear_buffer(request, ip):
    
#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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

#  # cek koneksi ke mesin finger
# def cek_koneksi(request):
    
#     user = request.session["user"]["nama"]

#     iduser = request.session["user"]["id"]
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
# 
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

# 
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

# 
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

# 
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

# 
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

# 
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

# 
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