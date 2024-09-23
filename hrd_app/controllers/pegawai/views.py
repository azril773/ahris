from hrd_app.controllers.lib import *

@login_required
def pegawai(request,sid):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.all().order_by('id')       
        # status = serialize("json",status)
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'status' : status,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/pegawai/[sid]/pegawai.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def pegawai_non_aktif(request,sid):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.all().order_by('id')       
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'status' : status,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/non_aktif/[sid]/non_aktif.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def edit_pegawai(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        pg = pegawai_db.objects.get(id=int(idp))
        counter = counter_db.objects.all().order_by('counter')
        divisi = divisi_db.objects.all().order_by('divisi')
        jabatan = jabatan_db.objects.all().order_by('jabatan')
        kk = kelompok_kerja_db.objects.all().order_by('kelompok')
        status = status_pegawai_db.objects.all().order_by('status')
        hr = hari_db.objects.all()
        keluarga = keluarga_db.objects.filter(pegawai_id=int(idp))
        kontak_lain = kontak_lain_db.objects.filter(pegawai_id=int(idp))
        pengalaman = pengalaman_db.objects.filter(pegawai_id=int(idp))
        pendidikan = pendidikan_db.objects.filter(pegawai_id=int(idp))
        try:
            pribadi = pribadi_db.objects.get(pegawai_id=pg.pk)
            pribadi.tgl_lahir = pribadi.tgl_lahir.strftime("%d-%m-%Y")
            pribadi.tinggi_badan = ".".join(str(pribadi.tinggi_badan).split(","))
            pribadi.berat_badan = ".".join(str(pribadi.berat_badan).split(","))
        except:
            pribadi = None
        today = date.today()
        krg = []
        kln = []
        pgl = []
        pdk = []

        for k in keluarga:
            obj = {
                "hubungan":k.hubungan,
                "nama":k.nama,
                "tgl_lahir":k.tgl_lahir.strftime("%d-%m-%Y"),
                "gender":k.gender,
                "gol_darah":k.gol_darah
            }
            krg.append(obj)

        
        for kl in kontak_lain:
            obj = {
                "hubungan":kl.hubungan,
                "nama":kl.nama,
                "gender":kl.gender,
                "phone":kl.phone
            }
            kln.append(obj)
        
        for pd in pendidikan:
            obj = {
                "pendidikan":pd.pendidikan,
                "id":1,
                "nama":pd.nama,
                "kota":pd.kota_id,
                "nama_koka":pd.kota.nama_koka,
                "dari_tahun":pd.dari_tahun.strftime("%d-%m-%Y"),
                "sampai_tahun":pd.sampai_tahun.strftime("%d-%m-%Y"),
                "jurusan":pd.jurusan,
                "gelar":pd.gelar
            }
            pdk.append(obj)

        for pn in pengalaman:
            print(pn.kota_id)
            obj = {
                "perusahaan":pn.perusahaan,
                "kota":pn.kota_id,
                "nama_koka":pn.kota.nama_koka,
                "dari_tahun":pn.dari_tahun.strftime("%d-%m-%Y"),
                "sampai_tahun":pn.sampai_tahun.strftime("%d-%m-%Y"),
                "jabatan":pn.jabatan
            }
            pgl.append(obj)
        # rsl = requests.get("https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json")
        # for r in rsl.json():
        #     resultk = requests.get('https://www.emsifa.com/api-wilayah-indonesia/api/regencies/'+r["id"]+'.json')
        #     for rk in resultk.json():
        #         kota_kabupaten_db(nama_kota_kabupaten=rk['name']).save()
        # kota_kabupaten = kota_kabupaten_db.objects.values("nama_kota_kabupaten")
        kota_kabupaten = kota_kabupaten_db.objects.all()
        # for k in kota_kabupaten:
        #     kota_kabupaten_db(nama_kota_kabupaten=k["nama_kota_kabupaten"]).save()
        if pg.tgl_masuk is not None:
            pg.tgl_masuk = pg.tgl_masuk.strftime("%d-%m-%Y")
        data = serialize("json",kota_kabupaten)
        data = {
            'akses' : akses,
            'id':idp,
            'dsid': dsid,
            'sid': pg.status_id,
            'counter': counter,
            'divisi': divisi,
            'jabatan': jabatan,
            "gender":["Laki-Laki","Perempuan"],
            'kk':kk,
            "pg_hr":pg.hari_off_id,
            'hr':hr,
            'pg':pg,
            "status":status,
            'today':datetime.strftime(today,'%d-%m-%Y'),
            'keluarga':krg,
            'kontak_lain':kln,
            'pengalaman':pgl,
            'pendidikan':pdk,
            'pribadi':pribadi,
            'idp':int(idp),
            'kota_kabupaten':kota_kabupaten,
            'modul_aktif' : 'Pegawai',
            'payroll':["Lainnya","HRD","Owner"],
            'goldarah':['O','A','B','AB'],
            'agama':['Islam','Katholik','Kristen','Hindu','Buddha','Konghucu'] 
        }
        print(data["pengalaman"])
        
        return render(request,'hrd_app/pegawai/epegawai/[sid]/edit.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@login_required
def epegawai(r,idp):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        user = akses_db.objects.get(pk=r.user.id)
        sid = user.sid_id
        nama = r.POST.get("nama")
        id = r.POST.get("id")
        gender = r.POST.get("gender")
        tgl_masuk = r.POST.get("tgl_masuk")
        nik = r.POST.get("nik")
        userid = r.POST.get("userid")
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

        print(hr,"ARI")
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
        print(alamat,phone,email,kota_lahir,tgl_lahir,tinggi,berat,goldarah)
        if alamat == '' or phone == '' or email == '' or kota_lahir == '' or tgl_lahir == '' or tinggi == '' or berat == '' or goldarah == '' or agama == '':
            return JsonResponse({"status":"error","msg":"data pribadi tidak boleh kosong"},status=400)
        keluarga = r.POST.get("keluarga")
        pihak = r.POST.get("pihak")
        pengalaman = r.POST.get("pengalaman")
        pendidikan = r.POST.get("pendidikan")
        keluarga = json.loads(keluarga)
        pihak = json.loads(pihak)
        pengalaman = json.loads(pengalaman)
        pendidikan = json.loads(pendidikan)
        try:
            pgw = pegawai_db.objects.get(pk=int(id))
        except:
            return JsonResponse({"status":"error"},status=400)
        status_pegawai = status_pegawai_db.objects.get(pk=status)
        if pribadi_db.objects.filter(~Q(pegawai__userid=userid),email=email).exists():
            return JsonResponse({"status":"error","msg":"Email sudah ada"},status=400)
        if pegawai_db.objects.filter(~Q(pk=int(idp)),userid=userid).exists():
            return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
        else:
            print("OKSODKSDOK")
            pegawai = pegawai_db.objects.filter(userid=userid).update(
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
                tgl_masuk=tgl_masuk,
                tgl_aktif=datetime.now().strftime('%Y-%m-%d'),
                hari_off_id=hr,
                kelompok_kerja_id=kk,
                sisa_cuti=12,
                counter_id=counter,
                add_by=r.user.username,
                edit_by=r.user.username

                # status
            )   

            

            # Pengalaman
            pengalaman_db.objects.filter(pegawai__userid=int(userid)).delete()
            for pgl in pengalaman:
                print(pgl)
                pengalaman_db(
                    pegawai_id=int(idp),
                    perusahaan=pgl['perusahaan'],
                    kota_id=pgl['kota'],
                    dari_tahun=datetime.strptime(pgl['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pgl['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jabatan=pgl['jabatan']
                ).save()


            # Pendidikan
            pendidikan_db.objects.filter(pegawai__userid=int(userid)).delete()
            for pdk in pendidikan:
                pendidikan_db(
                    pegawai_id=int(idp),
                    pendidikan=pdk['pendidikan'],
                    nama=pdk['nama'],
                    kota_id=pdk['kota'],
                    dari_tahun=datetime.strptime(pdk['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pdk['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jurusan=pdk['jurusan'],
                    gelar=pdk['gelar']
                ).save()


            # Tambah Pihak Lain
            pgw = pegawai_db.objects.get(userid=userid)
            kontak_lain_db.objects.filter(pegawai__userid=int(userid)).delete()
            for p in pihak:
                kontak_lain_db(
                pegawai_id=int(pgw.pk),
                hubungan = p['hubungan'],
                nama = p['nama'],
                gender = p['gender'],
                phone = p['phone']
                ).save()
            

            # Tambah Keluarga
            keluarga_db.objects.filter(pegawai__userid=int(userid)).delete()
            for k in keluarga:
                print(k)
                if k["hubungan"] != "" and k["nama"] != "" and k["tgl_lahir"] != "Invalid date" and k["tgl_lahir"] != "" and "gender" != "" and k["gol_darah"] != "":
                    keluarga_db(
                        pegawai_id=int(pgw.pk),
                        hubungan = k['hubungan'],
                        nama = k["nama"],
                        tgl_lahir = datetime.strptime(k['tgl_lahir'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                        gender = k['gender'],
                        gol_darah = k['gol_darah']
                    ).save()
                else:
                    pass

            # Tambah Data Pribadi
            pribadi = pribadi_db.objects.filter(pegawai_id=id)
            if len(pribadi) > 0:
                print(tinggi)
                pribadi_db.objects.filter(pegawai_id=id).update(
                    pegawai_id=int(pgw.pk),
                    alamat=alamat,
                    phone=phone,
                    email=email,
                    kota_lahir=kota_lahir,
                    tgl_lahir=tgl_lahir,
                    tinggi_badan=tinggi,
                    berat_badan=berat,
                    gol_darah=goldarah,
                    agama=agama
                )
            else: 
                pribadi_db(
                    pegawai_id=int(pgw.pk),
                    alamat=alamat,
                    phone=phone,
                    email=email,
                    kota_lahir=kota_lahir,
                    tgl_lahir=tgl_lahir,
                    tinggi_badan=tinggi,
                    berat_badan=berat,
                    gol_darah=goldarah,
                    agama=agama
                ).save()

            status= 'OK'
        print("OK")
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)

@login_required
def tpegawai(r):
    iduser = r.user.id

    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id

        counter = counter_db.objects.all().order_by('counter')
        divisi = divisi_db.objects.all().order_by('divisi')
        jabatan = jabatan_db.objects.all().order_by('jabatan')
        kk = kelompok_kerja_db.objects.all().order_by('kelompok')
        status = status_pegawai_db.objects.all().order_by('status')
        hr = hari_db.objects.all()

        kota_kabupaten = kota_kabupaten_db.objects.all()
        
        data = {
            'akses' : akses,
            'dsid': dsid,
            "counter":counter,
            "divisi":divisi,
            "jabatan":jabatan,
            'status':status,
            "kota_kabupaten":kota_kabupaten,
            "kk":kk,
            "hr":hr
        }
    return render(r,"hrd_app/pegawai/tpegawai/tambah.html",data)

@login_required
def tambah_pegawai(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        user = akses_db.objects.get(pk=r.user.id)
        sid = user.sid_id
        nama = r.POST.get("nama")
        gender = r.POST.get("gender")
        tgl_masuk = r.POST.get("tgl_masuk")
        nik = r.POST.get("nik")
        userid = r.POST.get("userid")
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
            status_pegawai = status_pegawai_db.objects.get(pk=status)
        except:
            status_pegawai = None
        if email == '' or alamat == '' or  phone == '' or kota_lahir == '' or tgl_lahir == 'Invalid date' or tgl_lahir == '' or tinggi == '' or berat == '' or goldarah == '' or agama == '':
            return JsonResponse({'status':"error","msg":"data pribadi tidak boleh kosong"},status=400,safe=False)

        if pribadi_db.objects.filter(email=email).exists():
            return JsonResponse({"status":"error","msg":"Email sudah ada"},status=400)

        if pegawai_db.objects.filter(userid=userid).exists():
            return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
        else:
            pegawai = pegawai_db(
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
            )            
            pegawai.save()


            # Tambah Pihak Lain
            pgw = pegawai_db.objects.get(userid=userid)
            for p in pihak:
                tkl = kontak_lain_db(
                pegawai_id=int(pgw.pk),
                hubungan = p['hubungan'],
                nama = p['nama'],
                gender = p['gender'],
                phone = p['phone']
                )
                tkl.save()
            

            # Tambah Keluarga
            for k in keluarga:
                tkeluarga = keluarga_db(
                    pegawai_id=int(pgw.pk),
                    hubungan = k['hubungan'],
                    nama = k["nama_keluarga"],
                    tgl_lahir = datetime.strptime(k['tgl_lahir_keluarga'],'%d-%m-%Y'),
                    gender = k['gender'],
                    gol_darah = k['goldarah']
                )
                tkeluarga.save()

            # Tambah Data Pribadi
            pribadi = pribadi_db(
                pegawai_id=int(pgw.pk),
                alamat=alamat,
                phone=phone,
                email=email,
                kota_lahir=kota_lahir,
                tgl_lahir=datetime.strptime(tgl_lahir,"%d-%m-%Y").strftime("%Y-%m-%d"),
                tinggi_badan=tinggi,
                berat_badan=berat,
                gol_darah=goldarah,
                agama=agama
            )
            print(alamat)
            for pgl in pengalaman:
                pengalaman_db(
                    pegawai_id=int(pgw.pk),
                    perusahaan=pgl['perusahaan'],
                    kota_id=pgl['kota'],
                    dari_tahun=datetime.strptime(pgl['dari_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    sampai_tahun=datetime.strptime(pgl['sampai_tahun'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                    jabatan=pgl['jabatan']
                ).save()
            
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
                ).save()
            pribadi.save()
            status = "ok"
            print(sid)
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)


@login_required
def getPegawai(r,idp):
    result = serialize("json",[pegawai_db.objects.get(pk=int(idp))])
    result = json.loads(result)
    print(result[0])
    return JsonResponse({"data":result[0]},status=200,safe=False)


@login_required
def tambah_keluarga(r, idp):

    nama_user = r.user.username
    print(r.POST)
    hubungan = r.POST.get('dhubungan_keluarga')
    dnama = r.POST.get('dnama_keluarga')
    tgl_lahir = r.POST.get('dtgl_lahir_keluarga')
    gender = r.POST.get('dgender_keluarga')
    gol_darah = r.POST.get('dgol_darah')
    
    if keluarga_db.objects.filter(hubungan=hubungan, nama=dnama, pegawai_id=int(idp)).exists():
        status = 'duplikat'
    else:
        tkeluarga = keluarga_db(
            pegawai_id=int(idp),
            hubungan = hubungan,
            nama = dnama,
            tgl_lahir = datetime.strptime(tgl_lahir,'%d-%m-%Y'),
            gender = gender,
            gol_darah = gol_darah
        )
        tkeluarga.save()
        
        didl = keluarga_db.objects.filter(pegawai_id=int(idp)).last()
        idl = didl.id
            
        status = 'ok'
        
    return JsonResponse({"status": status, "idl":idl, "hub":hubungan, "dnama":dnama, "tlahir":tgl_lahir, "gender":gender, "goldarah":gol_darah})


@login_required
def tambah_kl(request, idp):
    nama_user = request.user.username
    
    hubungan = request.POST.get('dhubungan_kl')
    dnama = request.POST.get('dnama_kl')
    gender = request.POST.get('dgender_kl')
    phone = request.POST.get('dphone')
    
    if kontak_lain_db.objects.filter(hubungan=hubungan, nama=dnama, pegawai_id=int(idp)).exists():
        status = 'duplikat'
    else:
        tkl = kontak_lain_db(
            pegawai_id=int(idp),
            hubungan = hubungan,
            nama = dnama,
            gender = gender,
            phone = phone
        )
        tkl.save()
        
        didl_kl = kontak_lain_db.objects.filter(pegawai_id=int(idp)).last()
        idl_kl = didl_kl.id
            
        status = 'ok'
        
    return JsonResponse({"status": status, "idl_kl":idl_kl, "hub_kl":hubungan, "dnama_kl":dnama, "gender_kl":gender, "dphone_kl":phone})


@login_required
def general_data(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'nama':pg.nama,
            'gender':pg.gender,
            'nik':pg.nik,
            'userid':pg.userid,
            'divisi':pg.divisi,
            'counter':pg.counter,
            'jabatan':pg.jabatan.jabatan,
            'tgl_masuk':pg.tgl_masuk,
            'off':pg.hari_off.hari,
            'kkerja':pg.kelompok_kerja,
            'shift':pg.shift,
            'rekening':pg.rekening,
            'payroll':pg.payroll_by,
            'nks':pg.no_bpjs_ks,
            'ntk':pg.no_bpjs_tk,
            'pks':pg.ks_premi,
            'ptk':pg.tk_premi,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/general_data.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def data_pribadi(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        pribadi = pribadi_db.objects.filter(pegawai_id=pg.pk)
        kontak_lain = kontak_lain_db.objects.filter(pegawai_id=pg.pk)
        keluarga = keluarga_db.objects.filter(pegawai_id=pg.pk)
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            "pribadi":pribadi,
            "keluarga":keluarga,
            "kontak_lain":kontak_lain,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/data_pribadi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def pendidikan_kerja(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id          
        pendidikan = pendidikan_db.objects.filter(pegawai_id=pg.pk)
        pdk = []
        for p in pendidikan:
            obj = p
            obj.kota = p.kota
            pdk.append(obj)
        pengalaman = pengalaman_db.objects.filter(pegawai_id=pg.pk)
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'pengalaman':pengalaman,
            'pendidikan':pendidikan,
            'modul_aktif' : 'Pegawai'
    }
        
        return render(request,'hrd_app/pegawai/pendidikan_pkerja.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def promosi_demosi(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.select_related("jabatan").get(id=int(idp))
        sid = pg.status_id          
        jabatan = jabatan_db.objects.all()
        print(jabatan)
        print(pg.jabatan_id)
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'jabatan_sebelum':pg.jabatan_id,
            'jabatan':jabatan,
            'pegawai':pegawai,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/promosi_demosi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')



@login_required
def tambah_prodemo(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        res = {"status":""}
        tgl = datetime.strptime(r.POST.get("tgl"),"%d-%m-%Y").strftime("%Y-%m-%d")
        status = r.POST.get("status")
        jabatan_seb = r.POST.get("jabatan_seb")
        jabatan_sek = r.POST.get("jabatan_sek")
        print(r.POST)
        idp = r.POST.get("id")

        if jabatan_seb ==  jabatan_sek:
            res["status"] = "Jabatan sama"
            return JsonResponse(res,status=400,safe=False)
        
        
        if status == "0":
            status = "Demosi"
        else:
            status = "Promosi"
        
        pgw = pegawai_db.objects.get(pk=int(idp))
        if not pgw:
            res['status'] = 'Pegawai tidak ada'
            return JsonResponse(res,status=400,safe=False)
        

        promosi_demosi_db(tgl=tgl,pegawai_id=int(idp),status=status,jabatan_sebelum_id=int(pgw.jabatan_id),jabatan_sekarang_id=int(jabatan_sek)).save()
        pg = pegawai_db.objects.get(pk=int(idp))
        pg.jabatan_id=int(jabatan_sek)
        pg.save()
        res["status"] = "Success"
        return JsonResponse(res,status=201,safe=False)

        

def promodemo_json(r,idp):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        status = r.POST.get("status")
        print(r.POST)
        if status == "0":
            result = promosi_demosi_db.objects.filter(pegawai_id=int(idp),status="demosi")
        else:
            result = promosi_demosi_db.objects.filter(pegawai_id=int(idp),status="promosi")
        
        rslt = []
        for r in result:
            obj = {
                "tgl":r.tgl,
                "jabatan_sebelum":r.jabatan_sebelum.jabatan,
                "jabatan_sekarang":r.jabatan_sekarang.jabatan
            }

            rslt.append(obj)
        return JsonResponse({'data':rslt},status=200,safe=False)


@login_required
def sangsi(request,idp):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        pg =pegawai_db.objects.get(id=int(idp))
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(request,'hrd_app/pegawai/sangsi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@login_required
def get_sangsi_pegawai(r,idp):
    sangsi = sangsi_db.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now()).last()
    if not sangsi:
        sangsi = {}
    else:
        sangsi = serialize("json",[sangsi])
        sangsi = json.loads(sangsi)[0]
    return JsonResponse({"data":sangsi},status=200,safe=False)

@login_required
def sangsi_json(r,idp):
    sangsi = sangsi_db.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now())
    result = []
    for s in sangsi:
        obj = {
            "tgl_berlaku":s.tgl_berlaku,
            "tgl_berakhir":s.tgl_berakhir,
            "status":s.status_sangsi,
            "deskripsi":s.deskripsi_pelanggaran
        }
        result.append(obj)
    return JsonResponse({"data":result})

@login_required
def tambah_sangsi(r,idp):

    # cek dari xmlhttprequest
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        tgl_berlaku = r.POST.get("tgl_berlaku")
        tgl_berakhir = r.POST.get("tgl_berakhir")
        status = r.POST.get("status")
        deskripsi = r.POST.get("deskripsi")

        # if status != "SP1" or status != "SP2" or status != "SP3":
        #      return JsonResponse({"status":"XIXIIX"},safe=False,status=400)
        # cek jika sp tersebut masih ada
        if sangsi_db.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now(),status_sangsi="SP3").exists():
            return JsonResponse({"status":"Kudunya dipecat ga si!"},safe=False,status=400)
        print(tgl_berakhir)
        if sangsi_db.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now(),status_sangsi=status).exists():
            return JsonResponse({"status":"Sangsi "+ status+" Sudah ada!"},safe=False,status=400)

    
        sangsi_db(
            pegawai_id=int(idp),
            tgl_berlaku=tgl_berlaku,
            tgl_berakhir=tgl_berakhir,
            status_sangsi=status,
            deskripsi_pelanggaran=deskripsi
        ).save()
        return JsonResponse({'status':"success create sangsi"},status=201,safe=False)


@login_required
def aktif_nonaktif(request):
    nama_user = request.user.username
    idp = request.POST.get('idp')
    nama_modul = request.POST.get('nama_modul')
    
    pg = pegawai_db.objects.get(id=int(idp))
    
    if nama_modul == "Non":
        pg.aktif = 0
    else:
        pg.aktif = 1
        
    pg.edit_by = nama_user
    pg.save()        
    
    status = 'ok'    
    
    return JsonResponse({"status": status})


@login_required
def pegawai_json(request, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        if int(sid) == 0:
            for p in pegawai_db.objects.select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(aktif=1):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y')   
                if p.counter:
                    counter = p.counter.counter
                else:
                    counter = None     
                pribadi = pribadi_db.objects.filter(pegawai_id=p.pk)
                if pribadi.exists():
                    email = pribadi[0].email
                else:
                    email = "" 
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':p.divisi.divisi,
                    'counter':counter,
                    'jabatan':p.jabatan.jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'email':email,
                    'kkerja':p.kelompok_kerja.kelompok,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id,
                }
                data.append(pg)
        else: 
            for p in pegawai_db.objects.select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(aktif=1, status_id=int(sid)):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y') 
                
                if p.counter:
                    counter = p.counter.counter
                else:
                    counter = None
                pribadi = pribadi_db.objects.filter(pegawai_id=p.pk)
                if pribadi.exists():
                    email = pribadi[0].email
                else:
                    email = "" 
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':p.divisi.divisi,
                    'counter':counter,
                    'jabatan':p.jabatan.jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    "email":email,
                    'kkerja':p.kelompok_kerja.kelompok,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id,
                }
                data.append(pg)       
                               
        return JsonResponse({"data": data})


@login_required
def non_aktif_json(request, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        if int(sid) == 0:
            for p in pegawai_db.objects.select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(aktif=0):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y')   
                                           
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':p.divisi.divisi,
                    'counter':p.counter.counter,
                    'jabatan':p.jabatan.jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'kkerja':p.kelompok_kerja.kelompok,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id
                }
                data.append(pg)
        else: 
            for p in pegawai_db.objects.select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(aktif=0, status_id=int(sid)):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y') 
                            
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':p.divisi.divisi,
                    'counter':p.counter.counter,
                    'jabatan':p.jabatan.jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'kkerja':p.kelompok_kerja.kelompok,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id
                }
                data.append(pg)       
                               
        return JsonResponse({"data": data})


@login_required
def detail_pegawai_json(request, idp):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
         
        p = pegawai_db.objects.filter(id=int(idp))
                        
        pg = {
            'idp':p.id,
            'nama':p.nama,
            'gender':p.gender,
            'nik':p.nik,
            'userid':p.userid,
            'divisi':p.divisi.divisi,
            'counter':p.counter,
            'jabatan':p.jabatan.jabatan,
            'tgl_masuk':p.tgl_masuk,
            'nbpjs_ks':p.no_bpjs_ks,
            'nbpjs_tk':p.no_bpjs_tk,
            'libur':p.hari_off.hari,
            'libur2':p.hari_off2.hari,
            'ks':p.ks_premi,
            'tk':p.tk_premi,
            'payroll':p.payroll_by,
            'rekening':p.rekening,
            'kkerja':p.kelompok_kerja.kelompok,
            'sisa_cuti':p.sisa_cuti
        }
        data.append(pg)       
                            
        return JsonResponse({"data": data})