from hrd_app.controllers.lib import *
from django.db import transaction
from django.core.files.storage import FileSystemStorage
import pathlib
import pandas as pd
import base64
@authorization(["*"])
def pegawai(r,sid):
    iduser = r.session["user"]["id"]
    print(iduser)
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        # for p in pegawai_db.objects.using(r.session["ccabang"]).all():
        #     if p.aktif == 0:
        #         pegawai_db_arsip(
        #             nama=p.nama,
        #             email=p.email,
        #             no_telp=p.no_telp,
        #             userid=p.userid,
        #             gender=p.gender,
        #             status=p.status,
        #             nik=p.nik,
        #             divisi=p.divisi,
        #             jabatan=p.jabatan,
        #             no_rekening=p.no_rekening,
        #             no_bpjs_ks=p.no_bpjs_ks,
        #             no_bpjs_tk=p.no_bpjs_tk,
        #             payroll_by=p.payroll_by,
        #             ks_premi=p.ks_premi,
        #             tk_premi=p.tk_premi,
        #             aktif=p.aktif,
        #             tgl_masuk=p.tgl_masuk,
        #             tgl_aktif=p.tgl_aktif,
        #             tgl_nonaktif=p.tgl_nonaktif,
        #             hari_off=p.hari_off,
        #             hari_off2=p.hari_off2,
        #             kelompok_kerja=p.kelompok_kerja,
        #             sisa_cuti=p.sisa_cuti,
        #             cuti_awal=p.cuti_awal,
        #             shift=p.shift,
        #             counter=p.counter,
        #             rekening=p.rekening,
        #             add_by=r.session["user"]["nama"],
        #         ).save(using=r.session["ccabang"])
        #         p.delete(using=r.session["ccabang"])
        # excel = pd.read_excel("static/ahris.xlsx")
        # data = []
        # for i in excel.iloc[:,0]:
        #     obj = {
        #         "id":i
        #     }
        #     data.append(obj)
        # # for d in data:
        # i = 0
        # for d in data:
        #     kelompok = excel.iloc[i,15]
        #     # 
        #     i += 1
        #     idp = d["id"]
        #     if kelompok == 0:
        #         pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(idp))
        #     else:
        #         pegawai = []
        #     # nama_user = r.session["user"]["nama"]
        #     if not pegawai:
        #         # return JsonResponse({"status":"error","msg":"Pegawai tidak ada"})
        #         continue
        #     p = pegawai[0]
        #     with transaction.atomic():
        #         pegawai_db_arsip(
        #             nama=p.nama,
        #             email=p.email,
        #             no_telp=p.no_telp,
        #             userid=p.userid,
        #             gender=p.gender,
        #             status=p.status,
        #             nik=p.nik,
        #             divisi=p.divisi,
        #             jabatan=p.jabatan,
        #             no_rekening=p.no_rekening,
        #             no_bpjs_ks=p.no_bpjs_ks,
        #             no_bpjs_tk=p.no_bpjs_tk,
        #             payroll_by=p.payroll_by,
        #             ks_premi=p.ks_premi,
        #             tk_premi=p.tk_premi,

        #             aktif=p.aktif,
        #             tgl_masuk=p.tgl_masuk,
        #             tgl_aktif=p.tgl_aktif,
        #             tgl_nonaktif=p.tgl_nonaktif,
        #             hari_off=p.hari_off,
        #             hari_off2=p.hari_off2,
        #             kelompok_kerja=p.kelompok_kerja,
        #             sisa_cuti=p.sisa_cuti,
        #             cuti_awal=p.cuti_awal,
        #             shift=p.shift,
        #             counter=p.counter,

        #             rekening=p.rekening,

        #             add_by="azril",
        #             edit_by="azril",
        #             add_date=datetime.now(),
        #             edit_date=datetime.now(),
        #             item_edit=p.item_edit
        #         ).save(using=r.session["ccabang"])

        #         parsip = pegawai_db_arsip.objects.using(r.session["ccabang"]).filter().last()
        #         # 
        #         pribadi = pribadi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
        #         if pribadi.exists():
        #             pribadi = pribadi[0]
        #             pribadi_db_arsip(
        #                 pegawai_id=parsip.pk,
        #                 alamat=pribadi.alamat,
        #                 phone=pribadi.phone,
        #                 email=pribadi.email,
        #                 kota_lahir=pribadi.kota_lahir,
        #                 tgl_lahir=pribadi.tgl_lahir,
        #                 tinggi_badan=pribadi.tinggi_badan,
        #                 berat_badan=pribadi.berat_badan,
        #                 gol_darah=pribadi.gol_darah,
        #                 agama=pribadi.agama
        #             ).save(using=r.session["ccabang"])
        #             pribadi.delete()
        #         # else:
        #         #     return JsonResponse({"status":"error","msg":"Data pribadi tidak ada"})



        #         keluarga = keluarga_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
        #         if keluarga.exists():
        #             for k in keluarga:
        #                 keluarga_db_arsip(
        #                     pegawai_id=parsip.pk,
        #                     hubungan=k.hubungan,
        #                     nama=k.nama,
        #                     tgl_lahir=k.tgl_lahir,
        #                     gender=k.gender,
        #                     gol_darah=k.gol_darah
        #                 ).save(using=r.session["ccabang"])
        #             keluarga.delete()
        #             # return JsonResponse({"status":"error","msg":"Data keluarga tidak ada"})


        #         kontak_lain = kontak_lain_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
        #         if kontak_lain.exists():
        #             for k in kontak_lain:
        #                 kontak_lain_db_arsip(
        #                     pegawai_id=parsip.pk,
        #                     hubungan=k.hubungan,
        #                     nama=k.nama,
        #                     gender=k.gender,
        #                     phone=k.phone
        #                 ).save(using=r.session["ccabang"])
        #             kontak_lain.delete()
        #             # return JsonResponse({"status":"error","msg":"Data kontak lain tidak ada"})


        #         pendidikan = pendidikan_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
        #         if pendidikan.exists():
        #             for pdk in pendidikan:
        #                 pendidikan_db_arsip(
        #                     pegawai_id=parsip.pk,
        #                     pendidikan=pdk.pendidikan,
        #                     nama=pdk.nama,
        #                     kota=pdk.kota,
        #                     dari_tahun=pdk.dari_tahun,
        #                     sampai_tahun=pdk.sampai_tahun,
        #                     jurusan=pdk.jurusan,
        #                     gelar=pdk.gelar
        #                 ).save(using=r.session["ccabang"])
        #             pendidikan.delete()
        #             # return JsonResponse({"status":"error","msg":"Data pendidikan tidak ada"})


        #         pengalaman = pengalaman_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
        #         if pengalaman.exists():
        #             for pgl in pengalaman:
        #                 pengalaman_db_arsip(
        #                     pegawai_id=parsip.pk,
        #                     perusahaan=pgl.perusahaan,
        #                     kota=pgl.kota,
        #                     dari_tahun=pgl.dari_tahun,
        #                     sampai_tahun=pgl.sampai_tahun,
        #                     jabatan=pgl.jabatan
        #                 ).save(using=r.session["ccabang"])
        #             pengalaman.delete()
        #             # return JsonResponse({"status":"error","msg":"Data pengalaman tidak ada"})


        #         promodemo = promosi_demosi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
        #         if promodemo.exists():
        #             for pdm in promodemo:

        #                 promosi_demosi_db_arsip(
        #                     tgl=pdm.tgl,
        #                     pegawai_id=parsip.pk,
        #                     status=pdm.status,
        #                     jabatan_sebelum=pdm.jabatan_sebelum,
        #                     jabatan_sekarang=pdm.jabatan_sekarang
        #                 ).save(using=r.session["ccabang"])
        #             promodemo.delete()

        #         sangsi = sangsi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
        #         # 
        #         if sangsi.exists():
        #             # 
        #             for s in sangsi:
        #                 sangsi_db_arsip(
        #                     pegawai_id=parsip.pk,
        #                     tgl_berlaku=s.tgl_berlaku,
        #                     tgl_berakhir=s.tgl_berakhir,
        #                     status_sangsi=s.status_sangsi,
        #                     deskripsi_pelanggaran=s.deskripsi_pelanggaran
        #                 ).save(using=r.session["ccabang"])
        #             sangsi.delete()



        #         # pegawai_db.objects.using(r.session["ccabang"]).filter(pk=pegawai.pk).delete()
        #         absensi = absensi_db.objects.filter(pegawai_id=p.pk)
        #         if absensi.exists():
        #             for b in absensi:
        #                 absensi_db_arsip(
        #                     pegawai=parsip.nama,
        #                     tgl_absen=b.tgl_absen,
        #                     masuk=b.masuk,
        #                     istirahat=b.istirahat,
        #                     kembali=b.kembali,
        #                     istirahat2=b.istirahat2,
        #                     kembali2=b.kembali2,
        #                     pulang=b.pulang,
        #                     masuk_b=b.masuk_b,
        #                     istirahat_b=b.istirahat,
        #                     kembali_b=b.kembali_b,
        #                     istirahat2_b=b.istirahat2_b,
        #                     kembali2_b=b.kembali2_b,
        #                     pulang_b=b.pulang_b,
        #                     keterangan_absensi=b.keterangan_absensi,
        #                     keterangan_ijin=b.keterangan_ijin,
        #                     keterangan_lain=b.keterangan_lain,
        #                     libur_nasional=b.libur_nasional,
        #                     insentif=b.insentif,
        #                     jam_masuk=b.jam_masuk,
        #                     lama_istirahat=b.lama_istirahat,
        #                     lama_istirahat2=b.lama_istirahat2,
        #                     jam_pulang=b.jam_pulang,
        #                     total_jam_kerja=b.total_jam_kerja,
        #                     total_jam_istirahat=b.total_jam_istirahat,
        #                     total_jam_istirahat2=b.total_jam_istirahat2,
        #                     lebih_jam_kerja=b.lebih_jam_kerja,
        #                     add_by="azril",
        #                     edit_by="azril",
        #                     add_date=b.add_date,
        #                     edit_date=datetime.now()
        #                 ).save(using=r.session["ccabang"])
        #         absensi.delete()


        #         pegawai.delete()
            # pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(d["id"])).update(kelompok_kerja_id=kelompok)
            # continue
            

        dsid = dakses.sid_id     
        
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi).distinct("status_id"):
            statusid.append(p.status_id)
            # print(p)
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")      
        # status = serialize("json",status)
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'status' : status,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(r,'hrd_app/pegawai/pegawai/[sid]/pegawai.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def pegawai_non_aktif(r,sid):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        statusid=[]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi).distinct("status_id"):
            statusid.append(p.status_id)
            # print(p)
        status = status_pegawai_db.objects.using(r.session["ccabang"]).filter(id__in=statusid).order_by("id")       
                
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'status' : status,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(r,'hrd_app/pegawai/non_aktif/[sid]/non_aktif.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["root","it"])
def edit_pegawai(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id     
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        pg = pegawai_db.objects.using(r.session["ccabang"]).get(id=int(idp))
        counter = counter_db.objects.using(r.session["ccabang"]).all().order_by('counter')
        divisi = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=aksesdivisi).order_by('divisi')
        jabatan = jabatan_db.objects.using(r.session["ccabang"]).all().order_by('jabatan')
        kk = kelompok_kerja_db.objects.using(r.session["ccabang"]).all().order_by('kelompok')
        status = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).all().order_by('status')
        hr = hari_db.objects.using(r.session["ccabang"]).all()
        keluarga = keluarga_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp))
        kontak_lain = kontak_lain_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp))
        pengalaman = pengalaman_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp))
        pendidikan = pendidikan_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp))
        print(pg.pk)
        try:
            pribadi = pribadi_db.objects.using(r.session["ccabang"]).get(pegawai_id=pg.pk)
            print(pribadi)
            pribadi.tgl_lahir = pribadi.tgl_lahir.strftime("%d-%m-%Y")
            pribadi.tinggi_badan = ".".join(str(pribadi.tinggi_badan).split(","))
            pribadi.berat_badan = ".".join(str(pribadi.berat_badan).split(","))
        except:
            pribadi = None
        print(pribadi)
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
                "gol_darah":k.gol_darah,
                "status_bpjs":k.status_bpjs if k.status_bpjs is not None else 0,
                "no_bpjs_ks":k.no_bpjs_ks if k.no_bpjs_ks is not None else 0
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
                "dari_tahun":pd.dari_tahun,
                "sampai_tahun":pd.sampai_tahun,
                "jurusan":pd.jurusan,
                "gelar":pd.gelar
            }
            pdk.append(obj)

        for pn in pengalaman:
            obj = {
                "perusahaan":pn.perusahaan,
                "kota":pn.kota_id,
                "nama_koka":pn.kota.nama_koka,
                "dari_tahun":pn.dari_tahun,
                "sampai_tahun":pn.sampai_tahun,
                "jabatan":pn.jabatan
            }
            pgl.append(obj)
        # rsl = requests.get("https://www.emsifa.com/api-wilayah-indonesia/api/provinces.json")
        # for r in rsl.json():
        #     resultk = requests.get('https://www.emsifa.com/api-wilayah-indonesia/api/regencies/'+r["id"]+'.json')
        #     for rk in resultk.json():
        #         kota_kabupaten_db(nama_kota_kabupaten=rk['name']).save(using=r.session["ccabang"])
        # kota_kabupaten = kota_kabupaten_db.objects.using(r.session["ccabang"]).values("nama_kota_kabupaten")
        kota_kabupaten = kota_kabupaten_db.objects.using(r.session["ccabang"]).all()
        shift = shift_db.objects.using(r.session["ccabang"]).all()
        # for k in kota_kabupaten:
        #     kota_kabupaten_db(nama_kota_kabupaten=k["nama_kota_kabupaten"]).save(using=r.session["ccabang"])
        if pg.tgl_masuk is not None:
            pg.tgl_masuk = pg.tgl_masuk.strftime("%d-%m-%Y")
        data = serialize("json",kota_kabupaten)
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
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
            'ca':pg.cuti_awal if pg.cuti_awal is not None else 0,
            "status":status,
            'today':datetime.strftime(today,'%d-%m-%Y'),
            'keluarga':krg,
            'kontak_lain':kln,
            'pengalaman':pgl,
            'pendidikan':pdk,
            'pribadi':pribadi,
            "shift":shift,
            "shift":shift,
            'idp':int(idp),
            'kota_kabupaten':kota_kabupaten,
            'modul_aktif' : 'Pegawai',
            'payroll':["Lainnya","HRD","Owner"],
            'goldarah':['O','A','B','AB'],
            'agama':['Islam','Katholik','Kristen','Hindu','Buddha','Konghucu'] 
        }
        
        return render(r,'hrd_app/pegawai/epegawai/[sid]/edit.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@authorization(["root","it"])
def epegawai(r,idp):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id = r.POST.get("id")
        with transaction.atomic(using=r.session["ccabang"]):
            try:
                fss = FileSystemStorage()
                file = r.FILES.get("file")
                user = akses_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])
                if not user.exists():
                    return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses"},status=400)
                user = user[0]
                print(r.POST)
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
                shift = r.POST.get("shift")
                print(shift)
                hr = r.POST.get("hr")
                ca = r.POST.get("ca")
                rek = r.POST.get("rek")
                payroll = r.POST.get("payroll")
                nks = r.POST.get("nks")
                ntk = r.POST.get("ntk")
                pks = r.POST.get("pks")
                ptk = r.POST.get("ptk")
                if nama == '' or gender == '' or tgl_masuk == 'Invalid date' or tgl_masuk == '' or nik == '' or userid == '' or div == '' or status == '' or kk == '' or hr == '' or ca == '' or payroll == '' or tgl_masuk is None or shift == "":
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
                if alamat == '' or phone == '' or email == '' or kota_lahir == '' or tgl_lahir == '' or agama == '':
                    return JsonResponse({"status":"error","msg":"data pribadi tidak boleh kosong"},status=400)
                keluarga = r.POST.get("keluarga")
                pihak = r.POST.get("pihak")
                pengalaman = r.POST.get("pengalaman")
                pendidikan = r.POST.get("pendidikan")
                keluarga = json.loads(keluarga)
                pihak = json.loads(pihak)
                pengalaman = json.loads(pengalaman)
                pendidikan = json.loads(pendidikan)
                id_user = r.session["user"]["id"]
                aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
                divisi = [div.divisi for div in aksesdivisi]
                print("COBA COBA")
                try:
                    pgw = pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(id),divisi__in=divisi).last()
                except Exception as e:
                    print(e)
                    return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
                if not pgw:
                    return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses ke pegawai ini"},status=400)
                status_pegawai = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).get(pk=status)
                if pribadi_db.objects.using(r.session["ccabang"]).filter(~Q(pegawai__userid=userid),email=email).exists():
                    return JsonResponse({"status":"error","msg":"Email sudah ada"},status=400)
                if pegawai_db.objects.using(r.session["ccabang"]).filter(~Q(pk=int(idp)),userid=userid).exists():
                    return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
                elif pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(~Q(pk=int(idp)),userid=userid).exists():
                    return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
                else:
                    url = pgw.profile_picture
                    if file == "undefined" or file == "null" or file is None: 
                        pass
                    else:
                        # Check for type image
                        if file.content_type == "image/jpeg" or file.content_type == "image/png" or file.content_type == "image/jpg":
                            # Check size of image
                            if file.size > 2000000:
                                transaction.set_rollback(True,using=r.session["ccabang"])
                                return JsonResponse({"status":'error',"msg":"File tidak boleh lebih dari 2 MB"},status=400)
                            

                            if pgw.profile_picture is not None:
                                if pgw.profile_picture[0] == "/":
                                    pp = pgw.profile_picture[1:]
                                else:
                                    pp = pgw.profile_picture
                                if pathlib.Path(pp).exists():
                                    os.remove(pp)
                            uploaded = fss.save(f'static/img/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")}_{"_".join(file.name.split(" "))}',file)
                            url = fss.url(uploaded)
                        else:
                            transaction.set_rollback(True,using=r.session["ccabang"])
                            return JsonResponse({"status":'error',"msg":"Pilih file dengan format jpeg, jpg, atau png"},status=400)
                    seri = serialize("json",[pgw])
                    seri = json.loads(seri)
                    seri[0]["fields"]["pegawai"] = pgw
                    seri[0]["fields"]["edit_by"] = r.session["user"]["nama"]
                    print(seri)
                    history_pegawai_db(**seri[0]["fields"]).save(using=r.session["ccabang"])
                    history = history_pegawai_db.objects.using(r.session["ccabang"]).filter().last()
                    pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(pgw.pk)).update(
                        nama=nama,
                        email=email,
                        gender=gender,
                        no_telp=phone,
                        userid=userid,
                        status=status_pegawai,
                        nik=nik,
                        divisi_id=div,
                        jabatan_id=jabatan,
                        no_rekening=rek,
                        no_bpjs_ks=nks,
                        no_bpjs_tk=ntk,
                        payroll_by=payroll,
                        profile_picture=url,
                        ks_premi=pks,
                        tk_premi=ptk,
                        aktif=1,
                        tgl_masuk=datetime.strptime(tgl_masuk,"%d-%m-%Y").strftime("%Y-%m-%d"),
                        tgl_aktif=datetime.now().strftime('%Y-%m-%d'),
                        hari_off_id=hr,
                        kelompok_kerja_id=kk,
                        shift=shift,
                        sisa_cuti=0,
                        cuti_awal=ca,
                        counter_id=counter,
                        add_by=r.session["user"]["nama"],
                        edit_by=r.session["user"]["nama"]

                        # status
                    )   

                    

                    # Pengalaman
                    pgldb = pengalaman_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).values("pegawai","perusahaan","kota","dari_tahun","sampai_tahun","jabatan")
                    dpgl = []
                    for hpgl in pgldb:
                        hpgl["history"] = history
                        dpgl.append(hpgl)
                    if len(dpgl) > 0:
                        [history_pengalaman_db(**dpg).save(using=r.session["ccabang"]) for dpg in dpgl]                            
                    pengalaman_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).delete()
                    for pgl in pengalaman:
                        print(pgl)
                        pengalaman_db(
                            pegawai_id=int(idp),
                            perusahaan=pgl['perusahaan'],
                            kota_id=pgl['kota'],
                            dari_tahun=pgl["dari_tahun"],
                            sampai_tahun=pgl["sampai_tahun"],
                            jabatan=pgl['jabatan']
                        ).save(using=r.session["ccabang"])


                    # Pendidikan
                    pdkdb = pendidikan_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).values("pegawai","pendidikan","nama","kota","dari_tahun","sampai_tahun","jurusan","gelar")
                    dpdk = []
                    for hpdk in pdkdb:
                        hpdk["fields"]["history"] = history
                        dpdk.append(hpdk["fields"])
                    if len(dpdk) > 0:
                        [history_pendidikan_db(**dpd).save(using=r.session["ccabang"]) for dpd in dpdk]
                    pendidikan_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).delete()
                    for pdk in pendidikan:
                        pendidikan_db(
                            pegawai_id=int(idp),
                            pendidikan=pdk['pendidikan'],
                            nama=pdk['nama'],
                            kota_id=pdk['kota'],
                            dari_tahun=pdk['dari_tahun'],
                            sampai_tahun=pdk['sampai_tahun'],
                            jurusan=pdk['jurusan'],
                            gelar=pdk['gelar']
                        ).save(using=r.session["ccabang"])


                    # Tambah Pihak Lain
                    kontak_lain = kontak_lain_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).values("pegawai","hubungan","nama","gender","phone")
                    dkontak_lain = []
                    for hkontak in kontak_lain:
                        hkontak["history"] = history
                        dkontak_lain.append(hkontak)
                    if len(dkontak_lain) > 0:
                        [history_kontak_lain_db(**d).save(using=r.session["ccabang"]) for d in dkontak_lain]


                    kontak_lain_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).delete()
                    for p in pihak:
                        kontak_lain_db(
                        pegawai_id=int(pgw.pk),
                        hubungan = p['hubungan'],
                        nama = p['nama'],
                        gender = p['gender'],
                        phone = p['phone']
                        ).save(using=r.session["ccabang"])


                    # Tambah Keluarga
                    klgdb = keluarga_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).values("pegawai","hubungan","nama","tgl_lahir","gender","gol_darah")
                    dkeluarga = []
                    print(klgdb)
                    for hklg in klgdb:
                        hklg["history"] = history
                        dkeluarga.append(hklg)
                    if len(dkeluarga) > 0:
                        [history_keluarga_db(**dkl).save(using=r.session["ccabang"]) for dkl in dkeluarga]

                    keluarga_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).delete()
                    for k in keluarga:
                        if k["hubungan"] != "" and k["nama"] != "" and k["tgl_lahir"] != "Invalid date" and k["tgl_lahir"] != "" and "gender" != "" and k["gol_darah"] != "":
                            keluarga_db(
                                pegawai_id=int(pgw.pk),
                                hubungan = k['hubungan'],
                                nama = k["nama"],
                                tgl_lahir = datetime.strptime(k['tgl_lahir'],'%d-%m-%Y'),
                                gender = k['gender'],
                                gol_darah = k['gol_darah'],
                                status_bpjs = k['status_bpjs'],
                                no_bpjs_ks = k['no_bpjs_ks'],
                            ).save(using=r.session["ccabang"])
                        else:
                            pass

                    # Tambah Data Pribadi
                    pribadi = pribadi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).values("pegawai","alamat","phone","email","kota_lahir","tgl_lahir","tinggi_badan","berat_badan","gol_darah","agama").last()
                    if pribadi is not None:
                        pribadi["history"] = history
                        history_pribadi_db(**pribadi).save(using=r.session["ccabang"])
                        pribadi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).update(
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
                        )
                    else: 
                        print("MASUKKKK")
                        pribadi_db(
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
                        ).save(using=r.session["ccabang"])
                        pribadi = pribadi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(pgw.pk)).values("pegawai","alamat","phone","email","kota_lahir","tgl_lahir","tinggi_badan","berat_badan","gol_darah","agama").last()
                        pribadi["history"] = history
                        print(pribadi)
                        history_pribadi_db(**pribadi).save(using=r.session["ccabang"])

                    status= 'OK'
            except Exception as e:
                print(e,"OSKOKDS")
                transaction.set_rollback(True,using=r.session['ccabang'])
                return JsonResponse({"status":"error","msg":"Terjadi kesalahan hubungi IT"},status=500)
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)

@authorization(["root","it"])
def tpegawai(r):
    iduser = r.session["user"]["id"]

    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id

        counter = counter_db.objects.using(r.session["ccabang"]).all().order_by('counter')
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        divisi = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=aksesdivisi).order_by('divisi')
        jabatan = jabatan_db.objects.using(r.session["ccabang"]).all().order_by('jabatan')
        kk = kelompok_kerja_db.objects.using(r.session["ccabang"]).all().order_by('kelompok')
        status = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).all().order_by('status')
        hr = hari_db.objects.using(r.session["ccabang"]).all()
        shift = shift_db.objects.using(r.session["ccabang"]).all()

        kota_kabupaten = kota_kabupaten_db.objects.using(r.session["ccabang"]).all()
        userid = ""
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
            "shift":shift,
            "hr":hr,
            "userid":userid
        }
    return render(r,"hrd_app/pegawai/tpegawai/tambah.html",data)

@authorization(["root","it"])
def tambah_pegawai(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        with transaction.atomic(using=r.session["ccabang"]):
            
            try:
                fss = FileSystemStorage()
                file = r.FILES.get("file")
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
                status = r.POST.get("status")
                div = r.POST.get("div")
                counter = r.POST.get("counter")
                jabatan = r.POST.get("jabatan")
                kk = r.POST.get("kk")
                shift = r.POST.get("shift")
                hr = r.POST.get("hr")
                ca = r.POST.get("ca")
                rek = r.POST.get("rek")
                payroll = r.POST.get("payroll")
                nks = r.POST.get("nks")
                ntk = r.POST.get("ntk")
                pks = r.POST.get("pks")
                ptk = r.POST.get("ptk")

                if nama == '' or gender == '' or tgl_masuk == 'Invalid date' or tgl_masuk == '' or nik == '' or userid == '' or div == '' or status == '' or kk == '' or hr == '' or ca == '' or payroll == '' or tgl_masuk is None or shift == "":
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
                id_user = r.session["user"]["id"]
                aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
                divisi = [d.pk for d in aksesdivisi]
                # 
                # return JsonResponse({"msg":"error"},status=400)
                if keluarga != "null":
                    keluarga = json.loads([])
                else:
                    keluarga = []
                

                if pihak != "null":
                    pihak = json.loads([])
                else:
                    pihak = []


                if pengalaman != "null":
                    pengalaman = json.loads([])
                else:
                    pengalaman = []
                

                if pendidikan != "null":
                    pendidikan = json.loads([])
                else:
                    pendidikan = []
                try:
                    status_pegawai = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).get(pk=status)
                except:
                    status_pegawai = None
                if alamat == '' or  phone == '' or kota_lahir == '' or tgl_lahir == 'Invalid date' or tgl_lahir == '' or agama == '':
                    return JsonResponse({'status':"error","msg":"data pribadi tidak boleh kosong"},status=400,safe=False)
                if email != "":
                    if pribadi_db.objects.using(r.session["ccabang"]).filter(email=email).exists():
                        return JsonResponse({"status":"error","msg":"Email sudah ada"},status=400)
                if pegawai_db.objects.using(r.session["ccabang"]).filter(userid=userid).exists():
                    return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
                elif pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(userid=userid).exists():
                    return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
                else:
                    url = None
                    if file == "undefined" or file == "null" or file is None or file == "None": 
                        pass
                    else:
                        if file.content_type == "image/jpeg" or file.content_type == "image/png" or file.content_type == "image/jpg":
                            if file.size > 2000000:
                                transaction.set_rollback(True,using=r.session["ccabang"])
                                return JsonResponse({"status":'error',"msg":"File tidak boleh lebih dari 2 MB"},status=400)
                            uploaded = fss.save(f'static/img/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")}_{"_".join(file.name.split(" "))}',file)
                            url = fss.url(uploaded)
                        else:
                            transaction.set_rollback(True,using=r.session["ccabang"])
                            return JsonResponse({"status":'error',"msg":"Pilih file dengan format jpeg, jpg, atau png"},status=400)
                    
                    pegawai_db(
                        nama=nama,
                        gender=gender,
                        email=email,
                        no_telp=phone,
                        userid=userid,
                        status=status_pegawai,
                        nik=nik,
                        divisi_id=div,
                        jabatan_id= jabatan ,
                        no_rekening=rek,
                        no_bpjs_ks=nks,
                        no_bpjs_tk=ntk,
                        payroll_by=payroll,
                        ks_premi=pks,
                        tk_premi=ptk,
                        aktif=1,
                        profile_picture=url,
                        tgl_masuk=datetime.strptime(str(tgl_masuk),'%d-%m-%Y').strftime("%Y-%m-%d"),
                        tgl_aktif=datetime.now().strftime('%Y-%m-%d'),
                        hari_off_id=hr,
                        kelompok_kerja_id=kk,
                        shift=shift,
                        sisa_cuti=0,
                        cuti_awal=ca,
                        counter_id=counter,
                        add_by=r.session["user"]["nama"],
                        edit_by=r.session["user"]["nama"]

                        # status
                    ).save(using=r.session["ccabang"])


                    # Tambah Pihak Lain
                    pgw = pegawai_db.objects.using(r.session["ccabang"]).get(userid=userid)
                    for p in pihak:
                        tkl = kontak_lain_db(
                        pegawai_id=int(pgw.pk),
                        hubungan = p['hubungan'],
                        nama = p['nama'],
                        gender = p['gender'],
                        phone = p['phone']
                        ).save(using=r.session["ccabang"])
                    
                    # Tambah Keluarga
                    for k in keluarga:
                        tkeluarga = keluarga_db(
                            pegawai_id=int(pgw.pk),
                            hubungan = k['hubungan'],
                            nama = k["nama_keluarga"],
                            tgl_lahir = datetime.strptime(k['tgl_lahir_keluarga'],'%d-%m-%Y').strftime("%Y-%m-%d"),
                            gender = k['gender'],
                            gol_darah = k['goldarah'],
                            status_bpjs = k["status_bpjs"],
                            no_bpjs_ks = k["no_bpjs_ks"]
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
                            dari_tahun=pgl['dari_tahun'],
                            sampai_tahun=pgl['sampai_tahun'],
                            jabatan=pgl['jabatan']
                        ).save(using=r.session["ccabang"])
                    
                    for pdk in pendidikan:
                        pendidikan_db(
                            pegawai_id=int(pgw.pk),
                            pendidikan=pdk['pendidikan'],
                            nama=pdk['nama'],
                            kota_id=pdk['kota'],
                            dari_tahun=pdk['dari_tahun'],
                            sampai_tahun=pdk['sampai_tahun'],
                            jurusan=pdk['jurusan'],
                            gelar=pdk['gelar']
                        ).save(using=r.session["ccabang"])
                    status = "ok"
                    
            except Exception as e:
                transaction.set_rollback(True,using=r.session["ccabang"])
                print(e,"OSKODKOSKD")
                return JsonResponse({"status":"error","msg":"Terjadi kesalahan hubungi IT"},status=500)
            
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)


@authorization(["*"])
def getPegawai(r,idp):
    id_user = r.session["user"]["id"]
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    result = serialize("json",[pegawai_db.objects.using(r.session["ccabang"]).get(pk=int(idp),divisi__in=divisi)])
    result = json.loads(result)
    return JsonResponse({"data":result[0]},status=200,safe=False)


@authorization(["*"])
def tambah_keluarga(r, idp):

    nama_user = r.session["user"]["nama"]
    hubungan = r.POST.get('dhubungan_keluarga')
    dnama = r.POST.get('dnama_keluarga')
    tgl_lahir = r.POST.get('dtgl_lahir_keluarga')
    gender = r.POST.get('dgender_keluarga')
    gol_darah = r.POST.get('dgol_darah')
    
    if keluarga_db.objects.using(r.session["ccabang"]).filter(hubungan=hubungan, nama=dnama, pegawai_id=int(idp)).exists():
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
        tkeluarga.save(using=r.session["ccabang"])
        
        didl = keluarga_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp)).last()
        idl = didl.id
            
        status = 'ok'
        
    return JsonResponse({"status": status, "idl":idl, "hub":hubungan, "dnama":dnama, "tlahir":tgl_lahir, "gender":gender, "goldarah":gol_darah})

@authorization(["*"])
def tambah_kl(r, idp):
    nama_user = r.session["user"]["nama"]
    
    hubungan = r.POST.get('dhubungan_kl')
    dnama = r.POST.get('dnama_kl')
    gender = r.POST.get('dgender_kl')
    phone = r.POST.get('dphone')
    
    if kontak_lain_db.objects.using(r.session["ccabang"]).filter(hubungan=hubungan, nama=dnama, pegawai_id=int(idp)).exists():
        status = 'duplikat'
    else:
        tkl = kontak_lain_db(
            pegawai_id=int(idp),
            hubungan = hubungan,
            nama = dnama,
            gender = gender,
            phone = phone
        )
        tkl.save(using=r.session["ccabang"])
        
        didl_kl = kontak_lain_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp)).last()
        idl_kl = didl_kl.id
            
        status = 'ok'
        
    return JsonResponse({"status": status, "idl_kl":idl_kl, "hub_kl":hubungan, "dnama_kl":dnama, "gender_kl":gender, "dphone_kl":phone})


@authorization(["*"])
def general_data(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        dsid = dakses.sid_id
        pg =pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'nama':pg.nama,
            'gender':pg.gender,
            'nik':pg.nik,
            'userid':pg.userid,
            'divisi':pg.divisi,
            'counter':pg.counter,
            'jabatan':pg.jabatan.jabatan if pg.jabatan is not None else "-",
            'tgl_masuk':pg.tgl_masuk,
            'off':pg.hari_off.hari,
            'kkerja':pg.kelompok_kerja,
            'shift':pg.shift,
            'rekening':pg.no_rekening,
            'payroll':pg.payroll_by,
            'nks':pg.no_bpjs_ks,
            'ntk':pg.no_bpjs_tk,
            'pks':pg.ks_premi,
            'ptk':pg.tk_premi,
            "pp":pg.profile_picture,
            'modul_aktif' : 'Pegawai',
            "aktif":1,
        }
        
        return render(r,'hrd_app/pegawai/general_data.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    

@authorization(["*"])
def general_data_nonaktif(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("non_aktif",sid=dsid)
        else:
            pg = pg[0]
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
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
            'rekening':pg.no_rekening,
            'payroll':pg.payroll_by,
            'nks':pg.no_bpjs_ks,
            'ntk':pg.no_bpjs_tk,
            'pks':pg.ks_premi,
            'ptk':pg.tk_premi,
            'modul_aktif' : 'Pegawai',
            "aktif":0,
        }
        
        return render(r,'hrd_app/pegawai/general_data.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def data_pribadi(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]


        pribadi = pribadi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        if pribadi.exists():
            pribadi = pribadi[0]
        else:
            pribadi = None


        kontak_lain = kontak_lain_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        if kontak_lain.exists():
            kontak_lain = kontak_lain
        else:
            kontak_lain = None


        keluarga = keluarga_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        if keluarga.exists():
            keluarga = keluarga
        else:
            keluarga = None
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            "pribadi":pribadi,
            "keluarga":keluarga,
            "kontak_lain":kontak_lain,
            'modul_aktif' : 'Pegawai',
            "aktif":1,
        }
        
        return render(r,'hrd_app/pegawai/data_pribadi.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')



@authorization(["*"])
def data_pribadi_nonaktif(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        dsid = dakses.sid_id   
        
        pg =pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]

        pribadi = pribadi_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        if pribadi.exists():
            pribadi = pribadi[0]
        else:
            pribadi = None

        kontak_lain = kontak_lain_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        if kontak_lain.exists():
            kontak_lain = kontak_lain
        else:
            kontak_lain = None

        keluarga = keluarga_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        if keluarga.exists():
            keluarga = keluarga
        else:
            keluarga = None
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            "pribadi":pribadi,
            "keluarga":keluarga,
            "kontak_lain":kontak_lain,
            'modul_aktif' : 'Pegawai',
            "aktif":0,
        }
        
        return render(r,'hrd_app/pegawai/data_pribadi.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')





def pendidikan_kerja(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]

        sid = pg.status_id          
        pendidikan = pendidikan_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        pdk = []
        for p in pendidikan:
            obj = p
            obj.kota = p.kota
            pdk.append(obj)
        pengalaman = pengalaman_db.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'pengalaman':pengalaman,
            'pendidikan':pendidikan,
            'modul_aktif' : 'Pegawai',
            "aktif":1,
    }
        
        return render(r,'hrd_app/pegawai/pendidikan_pkerja.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')




def pendidikan_kerja_nonaktif(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]


        sid = pg.status_id          
        pendidikan = pendidikan_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        pdk = []
        for p in pendidikan:
            obj = p
            obj.kota = p.kota
            pdk.append(obj)
        pengalaman = pengalaman_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=pg.pk)
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'pengalaman':pengalaman,
            'pendidikan':pendidikan,
            'modul_aktif' : 'Pegawai',
            "aktif":0,
    }
        
        return render(r,'hrd_app/pegawai/pendidikan_pkerja.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')



def promosi_demosi(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db.objects.using(r.session["ccabang"]).select_related("jabatan").filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]

        sid = pg.status_id          
        jabatan = jabatan_db.objects.using(r.session["ccabang"]).all()
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'jabatan_sebelum':pg.jabatan_id,
            'jabatan':jabatan,
            'pegawai':pegawai,
            'modul_aktif' : 'Pegawai',
            "aktif":1,
        }
        
        return render(r,'hrd_app/pegawai/promosi_demosi.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    


# 
# def promosi_demosi(r,idp):
#     iduser = r.session["user"]["id"]
        
#     if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
#         dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
#         akses = dakses.akses
           
#         dsid = dakses.sid_id   
        
#         pg =pegawai_db.objects.using(r.session["ccabang"]).select_related("jabatan").get(id=int(idp))
#         sid = pg.status_id          
#         jabatan = jabatan_db.objects.using(r.session["ccabang"]).all()
#         data = {
#             'akses' : akses,
#             'dsid': dsid,
#             'sid': int(sid),
#             'idp': idp,
#             'jabatan_sebelum':pg.jabatan_id,
#             'jabatan':jabatan,
#             'pegawai':pegawai,
#             'modul_aktif' : 'Pegawai',
#             "aktif":1,
#         }
        
#         return render(r,'hrd_app/pegawai/promosi_demosi.html', data)
        
#     else:    
#         messages.info(r, 'Data akses Anda belum di tentukan.')        
#         return redirect('beranda')



def promosi_demosi_nonaktif(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db_arsip.objects.using(r.session["ccabang"]).select_related("jabatan").filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]

        sid = pg.status_id          
        jabatan = jabatan_db.objects.using(r.session["ccabang"]).all()
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'jabatan_sebelum':pg.jabatan_id,
            'jabatan':jabatan,
            'pegawai':pegawai,
            'modul_aktif' : 'Pegawai',
            "aktif":0,
        }
        
        return render(r,'hrd_app/pegawai/promosi_demosi.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    


# 
# def promosi_demosi_nonaktif(r,idp):
#     iduser = r.session["user"]["id"]
        
#     if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
#         dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
#         akses = dakses.akses
           
#         dsid = dakses.sid_id   
        
#         pg =pegawai_db_arsip.objects.using(r.session["ccabang"]).select_related("jabatan").get(id=int(idp))
#         sid = pg.status_id          
#         jabatan = jabatan_db.objects.using(r.session["ccabang"]).all()
#         data = {
#             'akses' : akses,
#             'dsid': dsid,
#             'sid': int(sid),
#             'idp': idp,
#             'jabatan_sebelum':pg.jabatan_id,
#             'jabatan':jabatan,
#             'pegawai':pegawai,
#             'modul_aktif' : 'Pegawai',
#             "aktif":0,
#         }
        
#         return render(r,'hrd_app/pegawai/promosi_demosi.html', data)
        
#     else:    
#         messages.info(r, 'Data akses Anda belum di tentukan.')        
#         return redirect('beranda')




def tambah_prodemo(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        res = {"status":""}
        tgl = datetime.strptime(r.POST.get("tgl"),"%d-%m-%Y").strftime("%Y-%m-%d")
        status = r.POST.get("status")
        jabatan_seb = r.POST.get("jabatan_seb")
        jabatan_sek = r.POST.get("jabatan_sek")
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        idp = r.POST.get("id")

        if jabatan_seb ==  jabatan_sek:
            res["status"] = "Jabatan sama"
            return JsonResponse(res,status=400,safe=False)
        
        
        if status == "0":
            status = "Demosi"
        else:
            status = "Promosi"
        
        pgw =pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        
        if not pgw.exists():
            return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses ke pegawai ini"},status=400)
        else:
            pgw = pgw[0]


        if not pgw:
            res['status'] = 'Pegawai tidak ada'
            return JsonResponse(res,status=400,safe=False)
        

        promosi_demosi_db(tgl=tgl,pegawai_id=int(idp),status=status,jabatan_sebelum_id=int(pgw.jabatan_id),jabatan_sekarang_id=int(jabatan_sek)).save(using=r.session["ccabang"])
        pg = pegawai_db.objects.using(r.session["ccabang"]).get(pk=int(idp))
        pg.jabatan_id=int(jabatan_sek)
        pg.save(using=r.session["ccabang"])
        res["status"] = "Success"
        return JsonResponse(res,status=201,safe=False)

        

def promodemo_json(r,idp,aktif):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        status = r.POST.get("status")
        if aktif == 1:
            if status == "0":
                result = promosi_demosi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp),status__regex=r"(?i)demosi")
            else:
                result = promosi_demosi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp),status__regex=r"(?i)promosi")
        else:
            if status == "0":
                result = promosi_demosi_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp),status__regex=r"(?i)demosi")
            else:
                result = promosi_demosi_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp),status__regex=r"(?i)promosi")

        rslt = []
        
        for r in result:
            obj = {
                "tgl":r.tgl,
                "jabatan_sebelum":r.jabatan_sebelum.jabatan,
                "jabatan_sekarang":r.jabatan_sekarang.jabatan
            }

            rslt.append(obj)
        return JsonResponse({'data':rslt},status=200,safe=False)



def sangsi(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]
        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'modul_aktif' : 'Pegawai',
            "aktif":1,
        }
        
        return render(r,'hrd_app/pegawai/sangsi.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


def sangsi_nonaktif(r,idp):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
           
        dsid = dakses.sid_id   
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("pegawai",sid=dsid)
        else:
            pg = pg[0]



        sid = pg.status_id          
                
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'sid': int(sid),
            'idp': idp,
            'modul_aktif' : 'Pegawai',
            "aktif":0,
        }
        
        return render(r,'hrd_app/pegawai/sangsi.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


def get_sangsi_pegawai(r,idp):
    sangsi = sangsi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now()).last()
    if not sangsi:
        sangsi = {}
    else:
        sangsi = serialize("json",[sangsi])
        sangsi = json.loads(sangsi)[0]
    return JsonResponse({"data":sangsi},status=200,safe=False)


def sangsi_json(r,idp,aktif):
    if aktif == 0:
        sangsi = sangsi_db_arsip.objects.filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now())
    else:
        sangsi = sangsi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now())
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
        if sangsi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now(),status_sangsi="SP3").exists():
            return JsonResponse({"status":"Pegawai memiliki SP 3 yang masih berlaku!"},safe=False,status=400)
        if sangsi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp),tgl_berakhir__gte=datetime.now(),status_sangsi=status).exists():
            return JsonResponse({"status":"Sangsi "+ status+" Sudah ada!"},safe=False,status=400)

    
        sangsi_db(
            pegawai_id=int(idp),
            tgl_berlaku=tgl_berlaku,
            tgl_berakhir=tgl_berakhir,
            status_sangsi=status,
            deskripsi_pelanggaran=deskripsi
        ).save(using=r.session["ccabang"])
        return JsonResponse({'status':"success create sangsi"},status=201,safe=False)



def aktif_nonaktif(r):
    nama_user = r.session["user"]["nama"]
    idp = r.POST.get('idp')
    nama_modul = r.POST.get('nama_modul')
    id_user = r.session["user"]["id"]
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    
    pg =pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
    if not pg.exists():
        return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses ke pegawai ini"},status=400)
    else:
        pg = pg[0]
    
    if nama_modul == "Non":
        pg.aktif = 0
    else:
        pg.aktif = 1
        
    pg.edit_by = nama_user
    pg.save(using=r.session["ccabang"])        
    
    status = 'ok'    
    
    return JsonResponse({"status": status})



def nonaktif(r):
    idp = r.POST.get('idp')
    id_user = r.session["user"]["id"]
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    
    pg =pegawai_db.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
    if not pg.exists():
        return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses ke pegawai ini"},status=400)
    else:
        pg = pg[0]
    nama_user = r.session["user"]["nama"]
    p = pg
    with transaction.atomic(using=r.session["ccabang"]):
        try:
            pegawai_db_arsip(
                nama=p.nama,
                email=p.email,
                no_telp=p.no_telp,
                userid=p.userid,
                gender=p.gender,
                status=p.status,
                nik=p.nik,
                divisi=p.divisi,
                jabatan=p.jabatan,
                no_rekening=p.no_rekening,
                no_bpjs_ks=p.no_bpjs_ks,
                no_bpjs_tk=p.no_bpjs_tk,
                payroll_by=p.payroll_by,
                ks_premi=p.ks_premi,
                tk_premi=p.tk_premi,

                aktif=p.aktif,
                tgl_masuk=p.tgl_masuk,
                tgl_aktif=p.tgl_aktif,
                tgl_nonaktif=p.tgl_nonaktif,
                hari_off=p.hari_off,
                hari_off2=p.hari_off2,
                kelompok_kerja=p.kelompok_kerja,
                sisa_cuti=p.sisa_cuti,
                cuti_awal=p.cuti_awal,
                shift=p.shift,
                counter=p.counter,
                tgl_cuti=p.tgl_cuti,
                expired=p.expired,
                profile_picture=p.profile_picture,
                rekening=p.rekening,

                add_by=nama_user,
                edit_by=nama_user,
                add_date=datetime.now(),
                edit_date=datetime.now(),
                item_edit=p.item_edit
            ).save(using=r.session["ccabang"])

            parsip = pegawai_db_arsip.objects.using(r.session["ccabang"]).filter().last()
            pribadi = pribadi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if pribadi.exists():
                pribadi = pribadi[0]
                pribadi_db_arsip(
                    pegawai_id=parsip.pk,
                    alamat=pribadi.alamat,
                    phone=pribadi.phone,
                    email=pribadi.email,
                    kota_lahir=pribadi.kota_lahir,
                    tgl_lahir=pribadi.tgl_lahir,
                    tinggi_badan=pribadi.tinggi_badan,
                    berat_badan=pribadi.berat_badan,
                    gol_darah=pribadi.gol_darah,
                    agama=pribadi.agama
                ).save(using=r.session["ccabang"])
                pribadi.delete()
            # else:
            #     return JsonResponse({"status":"error","msg":"Data pribadi tidak ada"})



            keluarga = keluarga_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if keluarga.exists():
                for k in keluarga:
                    keluarga_db_arsip(
                        pegawai_id=parsip.pk,
                        hubungan=k.hubungan,
                        nama=k.nama,
                        tgl_lahir=k.tgl_lahir,
                        gender=k.gender,
                        gol_darah=k.gol_darah
                    ).save(using=r.session["ccabang"])
                keluarga.delete()
                # return JsonResponse({"status":"error","msg":"Data keluarga tidak ada"})


            kontak_lain = kontak_lain_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if kontak_lain.exists():
                for k in kontak_lain:
                    kontak_lain_db_arsip(
                        pegawai_id=parsip.pk,
                        hubungan=k.hubungan,
                        nama=k.nama,
                        gender=k.gender,
                        phone=k.phone
                    ).save(using=r.session["ccabang"])
                kontak_lain.delete()
                # return JsonResponse({"status":"error","msg":"Data kontak lain tidak ada"})


            pendidikan = pendidikan_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if pendidikan.exists():
                for pdk in pendidikan:
                    pendidikan_db_arsip(
                        pegawai_id=parsip.pk,
                        pendidikan=pdk.pendidikan,
                        nama=pdk.nama,
                        kota=pdk.kota,
                        dari_tahun=pdk.dari_tahun,
                        sampai_tahun=pdk.sampai_tahun,
                        jurusan=pdk.jurusan,
                        gelar=pdk.gelar
                    ).save(using=r.session["ccabang"])
                pendidikan.delete()
                # return JsonResponse({"status":"error","msg":"Data pendidikan tidak ada"})


            pengalaman = pengalaman_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if pengalaman.exists():
                for pgl in pengalaman:
                    pengalaman_db_arsip(
                        pegawai_id=parsip.pk,
                        perusahaan=pgl.perusahaan,
                        kota=pgl.kota,
                        dari_tahun=pgl.dari_tahun,
                        sampai_tahun=pgl.sampai_tahun,
                        jabatan=pgl.jabatan
                    ).save(using=r.session["ccabang"])
                pengalaman.delete()
                # return JsonResponse({"status":"error","msg":"Data pengalaman tidak ada"})


            promodemo = promosi_demosi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if promodemo.exists():
                for pdm in promodemo:

                    promosi_demosi_db_arsip(
                        tgl=pdm.tgl,
                        pegawai_id=parsip.pk,
                        status=pdm.status,
                        jabatan_sebelum=pdm.jabatan_sebelum,
                        jabatan_sekarang=pdm.jabatan_sekarang
                    ).save(using=r.session["ccabang"])
                promodemo.delete()

            sangsi = sangsi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if sangsi.exists():
                
                for s in sangsi:
                    sangsi_db_arsip(
                        pegawai_id=parsip.pk,
                        tgl_berlaku=s.tgl_berlaku,
                        tgl_berakhir=s.tgl_berakhir,
                        status_sangsi=s.status_sangsi,
                        deskripsi_pelanggaran=s.deskripsi_pelanggaran
                    ).save(using=r.session["ccabang"])
                sangsi.delete()



            absensi = absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if absensi.exists():
                for b in absensi:
                    absensi_db_arsip(
                        pegawai=parsip.nama,
                        tgl_absen=b.tgl_absen,
                        masuk=b.masuk,
                        istirahat=b.istirahat,
                        kembali=b.kembali,
                        istirahat2=b.istirahat2,
                        kembali2=b.kembali2,
                        pulang=b.pulang,
                        masuk_b=b.masuk_b,
                        istirahat_b=b.istirahat,
                        kembali_b=b.kembali_b,
                        istirahat2_b=b.istirahat2_b,
                        kembali2_b=b.kembali2_b,
                        pulang_b=b.pulang_b,
                        keterangan_absensi=b.keterangan_absensi,
                        keterangan_ijin=b.keterangan_ijin,
                        keterangan_lain=b.keterangan_lain,
                        libur_nasional=b.libur_nasional,
                        insentif=b.insentif,
                        jam_masuk=b.jam_masuk,
                        lama_istirahat=b.lama_istirahat,
                        lama_istirahat2=b.lama_istirahat2,
                        jam_pulang=b.jam_pulang,
                        total_jam_kerja=b.total_jam_kerja,
                        total_jam_istirahat=b.total_jam_istirahat,
                        total_jam_istirahat2=b.total_jam_istirahat2,
                        lebih_jam_kerja=b.lebih_jam_kerja,
                        add_by=nama_user,
                        edit_by=nama_user,
                        add_date=b.add_date,
                        edit_date=datetime.now()
                    ).save(using=r.session["ccabang"])
            absensi.delete()


            p.delete()
        except Exception as e:
            print(e)
            transaction.set_rollback(True,using=r.session["ccabang"])
            return JsonResponse({"status":"error","msg":"Terjadi kesalahan"})
    status = 'ok'
    return JsonResponse({"status": status})



def aktif(r):
    idp = r.POST.get('idp')
    nama_user = r.session["user"]["nama"]
    id_user = r.session["user"]["id"]
    aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    divisi = [div.divisi for div in aksesdivisi]
    
    pg =pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
    if not pg.exists():
        return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses ke pegawai ini"},status=400)
    else:
        pg = pg[0]
    p = pg
    with transaction.atomic(using=r.session["ccabang"]):
        try:
            pegawai_db(
                nama=p.nama,
                email=p.email,
                no_telp=p.no_telp,
                userid=p.userid,
                gender=p.gender,
                status=p.status,
                nik=p.nik,
                divisi=p.divisi,
                jabatan=p.jabatan,
                no_rekening=p.no_rekening,
                no_bpjs_ks=p.no_bpjs_ks,
                no_bpjs_tk=p.no_bpjs_tk,
                payroll_by=p.payroll_by,
                ks_premi=p.ks_premi,
                tk_premi=p.tk_premi,
                tgl_cuti=p.tgl_cuti,
                expired=p.expired,
                profile_picture=p.profile_picture,

                aktif=p.aktif,
                tgl_masuk=p.tgl_masuk,
                tgl_aktif=p.tgl_aktif,
                tgl_nonaktif=p.tgl_nonaktif,
                hari_off=p.hari_off,
                hari_off2=p.hari_off2,
                kelompok_kerja=p.kelompok_kerja,
                sisa_cuti=p.sisa_cuti,
                cuti_awal=p.cuti_awal,
                shift=p.shift,
                counter=p.counter,

                rekening=p.rekening,

                add_by=nama_user,
                edit_by=nama_user,
                add_date=datetime.now(),
                edit_date=datetime.now(),
                item_edit=p.item_edit
            ).save(using=r.session["ccabang"])

            pga = pegawai_db.objects.using(r.session["ccabang"]).filter().last()
            pribadi = pribadi_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if pribadi.exists():
                pribadi = pribadi[0]
                pribadi_db(
                    pegawai_id=pga.pk,
                    alamat=pribadi.alamat,
                    phone=pribadi.phone,
                    email=pribadi.email,
                    kota_lahir=pribadi.kota_lahir,
                    tgl_lahir=pribadi.tgl_lahir,
                    tinggi_badan=pribadi.tinggi_badan,
                    berat_badan=pribadi.berat_badan,
                    gol_darah=pribadi.gol_darah,
                    agama=pribadi.agama
                ).save(using=r.session["ccabang"])
                pribadi.delete()
            # else:
            #     return JsonResponse({"status":"error","msg":"Data pribadi tidak ada"})



            keluarga = keluarga_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if keluarga.exists():
                for k in keluarga:
                    keluarga_db(
                        pegawai_id=pga.pk,
                        hubungan=k.hubungan,
                        nama=k.nama,
                        tgl_lahir=k.tgl_lahir,
                        gender=k.gender,
                        gol_darah=k.gol_darah
                    ).save(using=r.session["ccabang"])
                keluarga.delete()
                # return JsonResponse({"status":"error","msg":"Data keluarga tidak ada"})


            kontak_lain = kontak_lain_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if kontak_lain.exists():
                for k in kontak_lain:
                    kontak_lain_db(
                        pegawai_id=pga.pk,
                        hubungan=k.hubungan,
                        nama=k.nama,
                        gender=k.gender,
                        phone=k.phone
                    ).save(using=r.session["ccabang"])
                kontak_lain.delete()
                # return JsonResponse({"status":"error","msg":"Data kontak lain tidak ada"})


            pendidikan = pendidikan_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if pendidikan.exists():
                for pdk in pendidikan:
                    pendidikan_db(
                        pegawai_id=pga.pk,
                        pendidikan=pdk.pendidikan,
                        nama=pdk.nama,
                        kota=pdk.kota,
                        dari_tahun=pdk.dari_tahun,
                        sampai_tahun=pdk.sampai_tahun,
                        jurusan=pdk.jurusan,
                        gelar=pdk.gelar
                    ).save(using=r.session["ccabang"])
                pendidikan.delete()
                # return JsonResponse({"status":"error","msg":"Data pendidikan tidak ada"})


            pengalaman = pengalaman_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if pengalaman.exists():
                for pgl in pengalaman:
                    pengalaman_db(
                        pegawai_id=pga.pk,
                        perusahaan=pgl.perusahaan,
                        kota=pgl.kota,
                        dari_tahun=pgl.dari_tahun,
                        sampai_tahun=pgl.sampai_tahun,
                        jabatan=pgl.jabatan
                    ).save(using=r.session["ccabang"])
                pengalaman.delete()
                # return JsonResponse({"status":"error","msg":"Data pengalaman tidak ada"})

            # pegawai_db.objects.using(r.session["ccabang"]).filter(pk=pegawai.pk).delete()

            promodemo = promosi_demosi_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if promodemo.exists():
                for pdm in promodemo:
                    promosi_demosi_db(
                        tgl=pdm.tgl,
                        pegawai_id=pga.pk,
                        status=pdm.status,
                        jabatan_sebelum=pdm.jabatan_sebelum,
                        jabatan_sekarang=pdm.jabatan_sekarang
                    ).save(using=r.session["ccabang"])
                promodemo.delete()


            sangsi = sangsi_db_arsip.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk)
            if sangsi.exists():
                for s in sangsi:
                    sangsi_db(
                        pegawai_id=pga.pk,
                        tgl_berlaku=s.tgl_berlaku,
                        tgl_berakhir=s.tgl_berakhir,
                        status_sangsi=s.status_sangsi,
                        deskripsi_pelanggaran=s.deskripsi_pelanggaran
                    ).save(using=r.session["ccabang"])
                sangsi.delete()

            pg.delete()
            status = 'ok'
        except Exception as e:
            print(e)
            return JsonResponse({"status":'error',"msg":"Terjadi kesalahan"},status=400)
            transaction.set_rollback(True,using=r.session["ccabang"])
    return JsonResponse({"status": "ok"})




def pegawai_json(r, sid):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        if int(sid) == 0:
            for p in pegawai_db.objects.using(r.session["ccabang"]).select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(divisi__in=divisi):
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y')   
                if p.counter is not None:
                    counter = p.counter.counter
                else:
                    counter = None     
                if p.divisi is not None:
                    divisi = p.divisi.divisi
                else:
                    divisi = None     
                if p.jabatan is not None:
                    jabatan = p.jabatan.jabatan
                else:
                    jabatan = None     
                if p.kelompok_kerja is not None:
                    kelompok_kerja = p.kelompok_kerja.kelompok
                else:
                    kelompok_kerja = None     
                email = p.email  
                if p.expired is not None:
                    expired_cuti = p.expired
                else:
                    expired_cuti = "-"
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':divisi,
                    'counter':counter,
                    'jabatan':jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'email':email,
                    "no_telp":p.no_telp,
                    'kkerja':kelompok_kerja,
                    'sisa_cuti':p.sisa_cuti,
                    "expired_cuti":expired_cuti if expired_cuti is not None else "",
                    'sid':p.status_id,
                }
                data.append(pg)
        else: 
            for p in pegawai_db.objects.using(r.session["ccabang"]).select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(status_id=int(sid),divisi__in=divisi):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y') 
                
                if p.counter is not None:
                    counter = p.counter.counter
                else:
                    counter = None     
                if p.divisi is not None:
                    divisi = p.divisi.divisi
                else:
                    divisi = None     
                if p.jabatan is not None:
                    jabatan = p.jabatan.jabatan
                else:
                    jabatan = None     
                if p.kelompok_kerja is not None:
                    kelompok_kerja = p.kelompok_kerja.kelompok
                else:
                    kelompok_kerja = None  
                if p.expired is not None:
                    expired_cuti = p.expired
                else:
                    expired_cuti = "-"
                email = p.email
                pg = { 
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':divisi,
                    'counter':counter,
                    'jabatan':jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    "email":email,
                    "no_telp":p.no_telp,
                    'kkerja':kelompok_kerja,
                    'sisa_cuti':p.sisa_cuti,
                    "expired_cuti":expired_cuti if expired_cuti is not None else "",
                    'sid':p.status_id,
                }
                data.append(pg)       
        return JsonResponse({"data": data},status=200)



def non_aktif_json(r, sid):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        data = []
        if int(sid) == 0:
            for p in pegawai_db_arsip.objects.using(r.session["ccabang"]).select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(divisi__in=divisi):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y')   
                if p.counter is not None:
                    counter = p.counter.counter
                else:
                    counter = None     
                if p.divisi is not None:
                    divisi = p.divisi.divisi
                else:
                    divisi = None     
                if p.jabatan is not None:
                    jabatan = p.jabatan.jabatan
                else:
                    jabatan = None     
                if p.kelompok_kerja is not None:
                    kelompok_kerja = p.kelompok_kerja.kelompok
                else:
                    kelompok_kerja = None
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':divisi,
                    'counter':counter,
                    'jabatan':jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'kkerja':kelompok_kerja,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id
                }
                data.append(pg)
        else: 
            for p in pegawai_db_arsip.objects.using(r.session["ccabang"]).select_related("jabatan","status","counter","hari_off","hari_off2","divisi","kelompok_kerja").filter(status_id=int(sid),divisi__in=divisi):
                
                if p.tgl_masuk is None:
                    tmasuk = None
                else:
                    tmasuk = datetime.strftime(p.tgl_masuk,'%d-%m-%Y') 
                if p.counter is not None:
                    counter = p.counter.counter
                else:
                    counter = None     
                if p.divisi is not None:
                    divisi = p.divisi.divisi
                else:
                    divisi = None     
                if p.jabatan is not None:
                    jabatan = p.jabatan.jabatan
                else:
                    jabatan = None     
                if p.kelompok_kerja is not None:
                    kelompok_kerja = p.kelompok_kerja.kelompok
                else:
                    kelompok_kerja = None
                pg = {
                    'idp':p.id,
                    'nama':p.nama,
                    'gender':p.gender,
                    'nik':p.nik,
                    'userid':p.userid,
                    'divisi':divisi,
                    'counter':counter,
                    'jabatan':jabatan,
                    'tgl_masuk':tmasuk,
                    'nbpjs_ks':p.no_bpjs_ks,
                    'nbpjs_tk':p.no_bpjs_tk,
                    'libur':p.hari_off.hari,
                    'ks':p.ks_premi,
                    'tk':p.tk_premi,
                    'payroll':p.payroll_by,
                    'kkerja':kelompok_kerja,
                    'sisa_cuti':p.sisa_cuti,
                    'sid':p.status_id
                }
                data.append(pg)       
                               
        return JsonResponse({"data": data})



def detail_pegawai_json(r, idp):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        id_user = r.session["user"]["id"]
        aksesdivisi = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        divisi = [div.divisi for div in aksesdivisi]
        
        pg =pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(id=int(idp),divisi__in=divisi)
        if not pg.exists():
            return JsonResponse({"status":"error","msg":"Anda tidak memiliki akses ke pegawai ini"},status=400)
        else:
            pg = pg[0]
        p = pg
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
            'rekening':p.no_rekening,
            'kkerja':p.kelompok_kerja.kelompok,
            'sisa_cuti':p.sisa_cuti
        }
        data.append(pg)       
                            
        return JsonResponse({"data": data})




def registrasi_pegawai(r):
    iduser = r.session["user"]["id"]
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses

        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).all().order_by('id')       
        # status = serialize("json",status)
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'dsid': dsid,
            'status' : status,
            'modul_aktif' : 'Pegawai'
        }
        
        return render(r,'hrd_app/pegawai/registrasi_pegawai.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


def rpm(r):
    iduser = r.session["user"]["id"]
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        
        mesin = mesin_db.objects.using(r.session["ccabang"]).all()
        data = {       
            'dsid': dsid,
            "mesin":mesin,
            'id':id,
            # 'userid':userid,
            'modul_aktif' : 'Dmesin'
        }

        
        
        return render(r,'hrd_app/mesin/dmesin.html',data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


def rp_mesin(r):
    iduser = r.session["user"]["id"]
        
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
            "divisi":divisi,
            'modul_aktif' : 'Mesin'     
        }
        
        return render(r,'hrd_app/pegawai/rp_mesin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    


def rp_cmesin(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(status="Active")
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1)
        divisi = divisi_db.objects.using(r.session["ccabang"]).all()
        data = {       
            'dsid': dsid,
            "mesin":mesin,
            "pegawai":pegawai,
            "divisi":divisi,
            'modul_aktif' : 'Mesin'     
        }
        
        return render(r,'hrd_app/pegawai/rp_cmesin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


def rp_form(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        user = r.session["user"]["nama"]

        iduser = r.session["user"]["id"]
        data_akses = akses_db.objects.using(r.session["ccabang"]).get(user=iduser)
        akses = data_akses.akses 
        dsid = data_akses.sid_id
        nama = r.POST.get("nama")
        userid = r.POST.get("userid")
        tipe = r.POST.get("tipe")
        mesin = r.POST.get("mesin")
        # if tipe != "rp_mesin":
        #     if akses == "admin" or akses == "root":
        #         level = r.POST.get("level")
        #         password = r.POST.get("password")
        #         if pegawai_db.objects.using(r.session["ccabang"]).filter(userid=userid).exists():
        #             messages.error(r,"Pegawai dengan userid tersebut sudah ada")
        #             return redirect("rp_mesin")
        #         if pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(userid=userid).exists():
        #             messages.error(r,"Pegawai dengan userid tersebut sudah ada")
        #             return redirect("rp_mesin")
        #         try:
        #             dmesin = mesin_db.objects.using(r.session["ccabang"]).get(pk=mesin)
                    
        #             id = dmesin.pk
        #             zk = ZK(dmesin.ipaddress,4370)
        #             conn = zk.connect()
        #             conn.disable_device()

        #             users = conn.get_users()
        #             uids = [user.uid for user in users]

        #             n_data = 1
        #             last_uid = sorted(uids)[-1]
        #             uid_ready = [uid for uid in range(uids[0], uids[-1] +1 ) if uid not in uids]
        #             if len(uid_ready) <= 0:
        #                 uid = last_uid + 1
        #                 if level == 1:
        #                     conn.set_user(uid=uid,name=nama,password=password,user_id=userid,privilege=const.USER_ADMIN,card=0,group_id='')
        #                 else:
        #                     conn.set_user(uid=uid,name=nama,password=password,user_id=userid,privilege=const.USER_DEFAULT,card=0,group_id='')
        #             else:
        #                 uid = uid_ready[0]
        #                 if level == 1:
        #                     conn.set_user(uid=uid,name=nama,password=password,user_id=userid,privilege=const.USER_ADMIN,card=0,group_id='')
        #                 else:
        #                     conn.set_user(uid=uid,name=nama,password=password,user_id=userid,privilege=const.USER_DEFAULT,card=0,group_id='')

        #             conn.enable_device()
        #             conn.disconnect()
        #         except Exception as e:
        #             messages.error(r,"Proccess terminate : {}".format(e))
        #             return redirect("rp_mesin")
        #         # finally:
        #         #     if conn:
        #         #         pass
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        counter = counter_db.objects.using(r.session["ccabang"]).all().order_by('counter')
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        divisi = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=aksesdivisi).order_by('divisi')
        jabatan = jabatan_db.objects.using(r.session["ccabang"]).all().order_by('jabatan')
        kk = kelompok_kerja_db.objects.using(r.session["ccabang"]).all().order_by('kelompok')
        status = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).all().order_by('status')
        hr = hari_db.objects.using(r.session["ccabang"]).all()
        kota_kabupaten = kota_kabupaten_db.objects.using(r.session["ccabang"]).all()

        shift = shift_db.objects.using(r.session["ccabang"]).all()
        
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
            "shift":shift,
            "kota_kabupaten":kota_kabupaten,
            "kk":kk,
            "hr":hr,
            "userid":userid,
            "nama":nama,
            "idmesin":mesin,
            'modul_aktif' : 'Pegawai'
        }
        return render(r,"hrd_app/pegawai/rp_form.html",data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


def tambah_pegawai_non_validasi(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        with transaction.atomic(using=r.session["ccabang"]) as wt:
            fss = FileSystemStorage()
            file = r.FILES.get("file")
            try:
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
                status = r.POST.get("status")
                div = r.POST.get("div")
                counter = r.POST.get("counter")
                jabatan = r.POST.get("jabatan")
                kk = r.POST.get("kk")
                shift = r.POST.get("shift")
                hr = r.POST.get("hr")
                ca = r.POST.get("ca")
                rek = r.POST.get("rek")
                payroll = r.POST.get("payroll")
                nks = r.POST.get("nks")
                ntk = r.POST.get("ntk")
                pks = r.POST.get("pks")
                ptk = r.POST.get("ptk")
                if nama == '' or gender == '' or tgl_masuk == 'Invalid date' or tgl_masuk == '' or nik == '' or userid == '' or div == '' or status == '' or kk == '' or hr == '' or ca == '' or payroll == '' or tgl_masuk is None or shift == "":
                    transaction.set_rollback(True,using=r.session["ccabang"])
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
                if keluarga != "null":
                    keluarga = json.loads(keluarga)
                else:
                    keluarga = []
                
 
                if pihak != "null":
                    pihak = json.loads(pihak)
                else:
                    pihak = []


                if pengalaman != "null":
                    pengalaman = json.loads(pengalaman)
                else:
                    pengalaman = []
                

                if pendidikan != "null":
                    pendidikan = json.loads(pendidikan)
                else:
                    pendidikan = []
                try:
                    status_pegawai = status_pegawai_db.objects.using(r.session["ccabang"]).using(r.session["ccabang"]).get(pk=status)
                except:
                    status_pegawai = None
                try:
                    id = r.POST.get("mesin")
                    
                    mesin = mesin_db.objects.using(r.session["ccabang"]).filter(id=int(id))
                    if not mesin.exists():
                        transaction.set_rollback(True,using=r.session["ccabang"])
                        return JsonResponse({"status":"error","msg":"Mesin tidak ada"},status=400)
                    conn = ZK(mesin[0].ipaddress,port=4370)
                    conn.connect()
                    conn.disable_device()


                    # users = conn.get_user_template(uid=int(uid))
                    users = conn.get_users()
                    usr = [u for u in users if u.user_id == userid]

                    conn.set_user(uid=usr[0].uid,name=nama,password=usr[0].password,user_id=usr[0].user_id,privilege=usr[0].privilege,card=0,group_id='')

                    users = [user for user in users if user.user_id == userid]
                    if len(users) <= 0:
                        transaction.set_rollback(True,using=r.session["ccabang"])
                        return JsonResponse({"status":"error","msg":"Userid tidak valid"},status=400)
                        
                    if len(users) > 0:
                        # datamesin = datamesin_db.objects.filter(userid=users[0].user_id)
                        # if datamesin.exists():
                        #     transaction.set_rollback(True)
                        #     return JsonResponse({"status":"error","msg":"Userid sudah ada di datamesin"},status=400)

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
                    print(e)
                    transaction.set_rollback(True,using=r.session["ccabang"])
                    return JsonResponse({"status":"error","msg":"Terjadi kesalahan"},status=500)
                if alamat == '' or  phone == '' or kota_lahir == '' or tgl_lahir == 'Invalid date' or tgl_lahir == '' or agama == '':
                    transaction.set_rollback(True,using=r.session["ccabang"])
                    return JsonResponse({'status':"error","msg":"data pribadi tidak boleh kosong"},status=400,safe=False)
                if email != "":
                    if pribadi_db.objects.using(r.session["ccabang"]).filter(email=email).exists():
                        transaction.set_rollback(True,using=r.session["ccabang"])
                        return JsonResponse({"status":"error","msg":"Email sudah ada"},status=400)

                if pegawai_db.objects.using(r.session["ccabang"]).filter(userid=userid).exists():
                    transaction.set_rollback(True,using=r.session["ccabang"])
                    return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
                elif pegawai_db_arsip.objects.using(r.session["ccabang"]).filter(userid=userid).exists():
                    transaction.set_rollback(True,using=r.session["ccabang"])
                    return JsonResponse({"status":"error","msg":"duplikat data"},status=400)
                else:
                    url = None
                    if file == "undefined" or file == "null" or file is None or file == "None": 
                        pass
                    else:
                        if file.content_type == "image/jpeg" or file.content_type == "image/png" or file.content_type == "image/jpg":
                            if file.size > 2000000:
                                transaction.set_rollback(True,using=r.session["ccabang"])
                                return JsonResponse({"status":'error',"msg":"File tidak boleh lebih dari 2 MB"},status=400)
                            uploaded = fss.save(f'static/img/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")}_{"_".join(file.name.split(" "))}',file)
                            url = fss.url(uploaded)
                        else:
                            transaction.set_rollback(True,using=r.session["ccabang"])
                            return JsonResponse({"status":'error',"msg":"Pilih file dengan format jpeg, jpg, atau png"},status=400)
                    pegawai_db(
                        nama=nama,
                        gender=gender,
                        email=email,
                        no_telp=phone,
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
                        profile_picture=url,
                        tk_premi=ptk,
                        aktif=1,
                        tgl_masuk=datetime.strptime(str(tgl_masuk),'%d-%m-%Y').strftime("%Y-%m-%d"),
                        tgl_aktif=datetime.now().strftime('%Y-%m-%d'),
                        hari_off_id=hr,
                        kelompok_kerja_id=kk,
                        shift=shift,
                        sisa_cuti=0,
                        cuti_awal=ca,
                        counter_id=counter,
                        add_by=r.session["user"]["nama"],
                        edit_by=r.session["user"]["nama"]
                    ).save(using=r.session["ccabang"])


                    # Tambah Pihak Lain
                    pgw = pegawai_db.objects.using(r.session["ccabang"]).get(userid=userid)
                    for p in pihak:
                        tkl = kontak_lain_db(
                        pegawai_id=int(pgw.pk),
                        hubungan = p['hubungan'],
                        nama = p['nama'],
                        gender = p['gender'],
                        phone = p['phone']
                        )
                        tkl.save(using=r.session["ccabang"])
                    

                    # Tambah Keluarga
                    for k in keluarga:
                        keluarga_db(
                            pegawai_id=int(pgw.pk),
                            hubungan = k['hubungan'],
                            nama = k["nama_keluarga"],
                            tgl_lahir = datetime.strptime(k['tgl_lahir_keluarga'],'%d-%m-%Y'),
                            gender = k['gender'],
                            gol_darah = k['goldarah'],
                            status_bpjs = k["status_bpjs"],
                            no_bpjs_ks = k["no_bpjs_ks"]
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
                        berat_badan=berat  if berat != "" else 0,
                        gol_darah=goldarah,
                        agama=agama
                    ).save(using=r.session["ccabang"])
                    for pgl in pengalaman:
                        pengalaman_db(
                            pegawai_id=int(pgw.pk),
                            perusahaan=pgl['perusahaan'],
                            kota_id=pgl['kota'],
                            dari_tahun=pgl['dari_tahun'],
                            sampai_tahun=pgl['sampai_tahun'],
                            jabatan=pgl['jabatan']
                        ).save(using=r.session["ccabang"])
                    
                    for pdk in pendidikan:
                        pendidikan_db(
                            pegawai_id=int(pgw.pk),
                            pendidikan=pdk['pendidikan'],
                            nama=pdk['nama'],
                            kota_id=pdk['kota'],
                            dari_tahun=pdk['dari_tahun'],
                            sampai_tahun=pdk['sampai_tahun'],
                            jurusan=pdk['jurusan'],
                            gelar=pdk['gelar']
                        ).save(using=r.session["ccabang"])
                    status = "ok"
            except Exception as e:
                print(e)
                transaction.set_rollback(True,using=r.session["ccabang"])
                return JsonResponse({"status":"error","msg":"Terjadi kesalahan hubungi IT"},status=500)
        return JsonResponse({'status':status,"sid":sid},status=200,safe=False)




def ambil_mesin(r):
    idmesin = r.POST.get("mesin")
    
    mesin = mesin_db.objects.using(r.session["ccabang"]).filter(pk=int(idmesin))
    if not mesin.exists():
        return JsonResponse({"status":"error","msg":"Mesin tidak ada"},status=400)
    try:
        datamesin = datamesin_db.objects.using(r.session["ccabang"]).all()
        dm = []
        for p in datamesin:
            dm.append(p.userid)
        obj = {}
        zk = ZK(mesin[0].ipaddress,4370,timeout=5)
        conn = zk.connect()
        conn.disable_device()
        users = conn.get_users()
        muserid = [u.user_id for u in users]
        userid = [{"userid":u.user_id,"uid":u.uid,"mesin":mesin[0].pk} for u in users if u.user_id not in dm]
        # userid.append({"userid":99902,"uid":})
        conn.enable_device()
        conn.disconnect()
        return JsonResponse({"status":"success","data":userid},status=200)
    except Exception as e:
        messages.error(r,"Proccess terminate : {}".format(e))
        return JsonResponse({"status":"error","msg":"Terjadi kesalahan hubungi IT"},status=500)

@authorization(["root","it"])
def spegawai_payroll(r):
    id_user = r.session["user"]["id"]
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user):
        akses = akses_db.objects.using(r.session["ccabang"]).get(user_id=id_user)
        akses = akses.akses
        pegawaip = pegawai_payroll_db.objects.using(f'p{r.session["ccabang"]}').all()
        pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
        for p in pegawai:
            if len([pe for pe in pegawaip if p.userid == pe.userid]) > 0:
                continue
            pegawai_payroll_db(
                id=p.pk,
                nama=p.nama,
                userid=p.userid,
                gender=p.gender,
                status=p.status,
                nik=p.nik,
                divisi=p.divisi,
                no_rekening=p.no_rekening,
                no_bpjs_ks=p.no_bpjs_ks,
                no_bpjs_tk=p.no_bpjs_tk,
                payroll_by=p.payroll_by,
                ks_premi=p.ks_premi,
                tk_premi=p.tk_premi,
                aktif=1,
                tgl_masuk=p.tgl_masuk,
                status_payroll=0,
                add_by="prog",
                edit_by="prog",
            ).save(using=f'p{r.session["ccabang"]}')
    else:
        pass



def upload_foto(r):
    file = r.FILES.get("file")
    fss = FileSystemStorage()
    upload = fss.save(f'static/img/{file.name}',file)
    url = fss.url(upload)
    print(url)
    print(upload)
    # file = open("static/img/coba.jpeg","wb")
    # file.write(foto)
    # print(foto)/


@authorization(["root","it"])
def history(r,sid):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    dsid = akses.sid_id
    aksesdiv = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    div = [div.divisi.pk for div in aksesdiv]
    pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=div).distinct("status_id")
    status = [p.status_id for p in pegawai]
    s_pegawai = status_pegawai_db.objects.using(r.session['ccabang']).filter(pk__in=status)
    data = {
        'akses' : akses.akses,
        "cabang":r.session["cabang"],
        "ccabang":r.session["ccabang"],
        "nama":r.session["user"]["nama"],
        'dsid': dsid,
        'sid': int(sid),
        "status":s_pegawai,
        'modul_aktif' : 'Pegawai'
    }
    return render(r,"hrd_app/pegawai/history/history.html",data)


@authorization(["root","it"])
def history_pegawai_json(r,sid):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.session["user"]["id"]
        akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
        data = []
        aksesdiv = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        div = [div.divisi.pk for div in aksesdiv]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=div,status_id=sid):
            # divisi = f'{p.divisi} / {p.counter}' if p.counter is not None else '' 
            if p.divisi is not None and p.counter is not None:
                divisi = f"{p.divisi.divisi} - {p.counter.counter}"
            elif p.divisi is not None:
                divisi = f"{p.divisi.divisi}"
            else:
                divisi = "-"
            obj = {
                "id":p.pk,
                "nama":p.nama,
                "nik":p.nik,
                "sid":p.status_id,
                "userid":p.userid,
                "divisi":divisi,
                "jabatan":p.jabatan.jabatan if p.jabatan is not None else "-",
                "hari_off":p.hari_off.hari
            }
            data.append(obj)
        print(data)
        return JsonResponse({"status":'success',"msg":"Berhasil ambil data pegawai","data":data},status=200)
    else:
        return JsonResponse({"status":"error","msg":"Terjadi Kesalahan"},status=400)
    
@authorization(["root","it"])
def detail_history(r,sid,idp):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    dsid = akses.sid_id
    aksesdiv = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    div = [div.divisi.pk for div in aksesdiv]
    pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=div).distinct("status_id")
    status = [p.status_id for p in pegawai]
    s_pegawai = status_pegawai_db.objects.using(r.session['ccabang']).filter(pk__in=status)
    pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(pk=int(idp),divisi_id__in=div).last()
    if not pegawai:
        messages.error(r,"Pegawai tidak ada")
        return redirect("history",sid=sid)
    data = {
        'akses' : akses,
        "cabang":r.session["cabang"],
        "ccabang":r.session["ccabang"],
        "nama":r.session["user"]["nama"],
        'dsid': dsid,
        'idp': idp,
        'sid': int(sid),
        "status":s_pegawai,
        'modul_aktif' : 'Pegawai'
    }
    return render(r,"hrd_app/pegawai/history/[sid]/[idp]/detail_history.html",data)
            
@authorization(["root","it"])
def detail_history_json(r,sid,idp):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session['ccabang']).filter(user_id=id_user).last()
    data = []
    for h in history_pegawai_db.objects.select_related("pegawai__divisi","pegawai__kelompok_kerja","pegawai").using(r.session["ccabang"]).filter(pegawai_id=int(idp)):
        obj = {
            "id":h.pk,
            "nama":h.pegawai.nama,
            "userid":h.pegawai.userid,
            "nik":h.pegawai.nik,
            "tgl_masuk":h.pegawai.tgl_masuk,
            "kk":h.pegawai.kelompok_kerja.kelompok if h.pegawai.kelompok_kerja is not None else "-",
            "divisi":h.pegawai.divisi.divisi if h.pegawai.divisi is not None else "",
            "edit_by":h.edit_by,
            "edit_date":h.edit_date
        }
        data.append(obj)
    return JsonResponse({"status":"success","msg":"Berhasil ambil data history","data":data},status=200)


@authorization(["root","it"])
def detail_data_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.session["user"]["id"]
        akses = akses_db.objects.using(r.session['ccabang']).filter(user_id=id_user).last()
        hid = r.POST.get("id")
        aksesdiv = akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
        div = [div.divisi_id for div in aksesdiv]
        history = history_pegawai_db.objects.select_related("pegawai__divisi").using(r.session["ccabang"]).filter(pk=int(hid),pegawai__divisi_id__in=div)
        data = []
        for h in history:
            obj = {
                "pegawai":h.pegawai_id,
                "nama":h.nama,
                "email":h.email,
                "no_telp":h.no_telp,
                "userid":h.userid,
                "gender":h.gender,
                "status":h.pegawai.status.status if h.pegawai.status is not None else "-",
                "nik":h.nik,
                "divisi":h.pegawai.divisi.divisi if h.pegawai.divisi is not None else "-",
                "jabatan":h.pegawai.jabatan.jabatan if h.pegawai.jabatan is not None else "-",
                "no_rekening":h.no_rekening,
                "no_bpjs_ks":h.no_bpjs_ks,
                "no_bpjs_tk":h.no_bpjs_tk,
                "payroll_by":h.payroll_by,
                "ks_premi":h.ks_premi,
                "tk_premi":h.tk_premi,
                "aktif":h.aktif,
                "tgl_masuk":h.tgl_masuk,
                "tgl_aktif":h.tgl_aktif,
                "tgl_nonaktif":h.tgl_nonaktif,
                "tgl_cuti":h.tgl_cuti,
                "expired":h.expired,
                "hari_off":h.pegawai.hari_off.hari if h.pegawai.hari_off is not None else "-",
                "hari_off2":h.pegawai.hari_off2.hari if h.pegawai.hari_off2 is not None else "-",
                "kelompok_kerja":h.pegawai.kelompok_kerja.kelompok if h.pegawai.kelompok_kerja is not None else "-",
                "sisa_cuti":h.sisa_cuti,
                "cuti_awal":h.cuti_awal,
                "shift":h.shift,
                "counter":h.pegawai.counter.counter if h.pegawai.counter is not None else "-",
                "profile_picture":h.profile_picture,
                "rekening":h.rekening,
                "add_by":h.add_by,
                "edit_by":h.edit_by,
                "add_date":h.add_date,
                "edit_date":h.edit_date,
                "item_edit":h.item_edit
            }
            data.append(obj)
        return JsonResponse({"status":'success',"msg":"Berhasil ambil data","data":data},status=200)
    else:
        return JsonResponse({"status":"error","msg":"Terjadi Kesalahan"},status=400)
    

        
@authorization(["root","it"])
def history_pribadi_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.session["user"]["id"]
        akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
        hid = r.POST.get("id")
        data = []
        for h in history_pribadi_db.objects.using(r.session["ccabang"]).filter(history_id=hid):
            obj = {
                "pegawai":h.pegawai,
                "alamat":h.alamat,
                "phone":h.phone,
                "email":h.email,
                "kota_lahir":h.kota_lahir,
                "tgl_lahir":h.tgl_lahir,
                "tinggi_badan":h.tinggi_badan,
                "berat_badan":h.berat_badan,
                "gol_darah":h.gol_darah,
                "agama":h.agama, 
            }
            data.append(obj)
        return JsonResponse({"status":'success','msg':"Berhasil ambil data","data":data},status=200)
        

@authorization(["root","it"])
def keluarga_data_json(r):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    hid = r.POST.get("id")
    keluarga = []
    for kp in history_keluarga_db.objects.using(r.session["ccabang"]).filter(history_id=hid):
        obj = {
            "pegawai":kp.pegawai if kp.pegawai is not None else '-',
            "hubungan":kp.hubungan if kp.hubungan is not None else "-",
            "nama":kp.nama if kp.nama is not None else "-", 
            "tgl_lahir":kp.tgl_lahir if kp.tgl_lahir is not None else "-",
            "gender":kp.gender if kp.gender is not None else '-',
            "gol_darah":kp.gol_darah if kp.gol_darah is not None else "-",
        }
        keluarga.append(obj)
    return JsonResponse({"status":'success',"msg":"Berhasil ambil data","data":keluarga},status=200)
    
@authorization(["root","it"])
def pihak_data_json(r):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    hid = r.POST.get("id")
    pihak = []
    for k in history_kontak_lain_db.objects.using(r.session["ccabang"]).filter(history_id=hid):
        obj  = {
            "pegawai":k.pegawai if k.pegawai is not None else "-",
            "hubungan":k.hubungan if k.hubungan is not None else "-",
            "nama":k.nama if k.nama is not None else "-",
            "gender":k.gender if k.gender is not None else "-",
            "phone":k.phone if k.phone is not None else "-",
        }
        pihak.append(obj)
    return JsonResponse({"status":'success',"msg":"Berhasil ambil data","data":pihak,"pihak":pihak},status=200)
    

@authorization(["root","it"])
def pengalaman_data_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.session["user"]["id"]
        akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
        hid = r.POST.get("id")
        pengalaman = []
        for pgl in history_pengalaman_db.objects.using(r.session['ccabang']).filter(history_id=hid):
            obj = {
                "pegawai":pgl.pegawai,
                "perusahaan":pgl.perusahaan,
                "kota":pgl.kota,
                "dari_tahun":pgl.dari_tahun,
                "sampai_tahun":pgl.sampai_tahun,
                "jabatan":pgl.jabatan,
            }
            pengalaman.append(obj)
        return JsonResponse({"status":"success","msg":"Berhasil ambil data","data":pengalaman},status=200)

@authorization(["root","it"])
def pendidikan_data_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.session["user"]["id"]
        akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
        hid = r.POST.get("id")
        pendidikan = []
        for pdk in history_pendidikan_db.objects.using(r.session["ccabang"]).filter(history_id=hid):
            obj = {
                "pegawai":pdk.pegawai,
                "pendidikan":pdk.pendidikan,
                "nama":pdk.nama,
                "kota":pdk.kota,
                "dari_tahun":pdk.dari_tahun,
                "sampai_tahun":pdk.sampai_tahun,
                "jurusan":pdk.jurusan,
                "gelar":pdk.gelar,
            }
            pendidikan.append(obj)
        return JsonResponse({"status":"success","msg":"Berhasil ambil data","data":pendidikan},status=200)
