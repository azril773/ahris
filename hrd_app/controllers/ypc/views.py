from hrd_app.controllers.lib import *

@login_required
def tlengkap(r,sid):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            # 'sid': sid,
            'sil': sid_lembur,
            # "pegawai":pegawai,
            'modul_aktif' : 'Laporan'
        }
        return render(r,"hrd_app/ypc/tlengkap.html",data)


@login_required
def tketerangan(r,sid):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        jenis_ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).all()  
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur,
            "jenis_ijin":jenis_ijin,
            # "pegawai":pegawai,
            'modul_aktif' : 'Laporan'
        }
        return render(r,"hrd_app/ypc/tketerangan.html",data)

@login_required
def terlambat(r,sid):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur,
            # "pegawai":pegawai,
            'modul_aktif' : 'Laporan'
        }
        return render(r,"hrd_app/ypc/terlambat.html",data)
    
    
@login_required
def tlengkap_json(r,sid):
    if r.headers["X-Requested_With"] == "XMLHttpRequest":
        today = datetime.now()
        tgl1 = r.POST.get("tgl1")
        tgl2 = r.POST.get("tgl2")
        if (tgl1 == "" and tgl2 == "") or (tgl1 is None and tgl2 is None):
            tgl2 = datetime.now()
            tgl1 = tgl2 - timedelta(days=1)
        else:
            tgl2 = datetime.strptime(tgl2,'%d-%m-%Y').date()
            tgl1 = datetime.strptime(tgl1,'%d-%m-%Y').date()
        hari = datetime.now().strftime("%A")
        hari = nama_hari(hari)
        data = []
        id_user = r.user.id
        div = [d.divisi for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)]
        if sid == 0:
            result = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__hari_off","pegawai__hari_off2","pegawai","pegawai__divisi").filter(~Q(pegawai__hari_off__hari=hari) | ~Q(pegawai__hari_off2__hari=hari) ,tgl_absen__range=[tgl1,tgl2],pegawai__divisi__in=div)
        else:
            result = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__hari_off","pegawai__hari_off2","pegawai","pegawai__divisi").filter(~Q(pegawai__hari_off__hari=hari) | ~Q(pegawai__hari_off2__hari=hari) ,tgl_absen__range=[tgl1,tgl2],pegawai__status_id=int(sid),pegawai__divisi__in=div)
        for ab in result:
            if (ab.masuk is not None and ab.pulang is not None and ab.istirahat is not None and ab.kembali is not None) or (ab.masuk_b is not None and ab.pulang_b is not None and ab.istirahat_b is not None and ab.kembali_b is not None):
                pass
            else:
                obj = {
                    "tanggal":ab.tgl_absen,
                    "pegawai":ab.pegawai.nama,
                    "nik":ab.pegawai.nik,
                    "shift":ab.pegawai.shift,
                    "divisi":ab.pegawai.divisi.divisi,
                    "masuk":ab.masuk if ab.masuk is not None else "-",
                    "istirahat":ab.istirahat if ab.istirahat is not None else "-",
                    "kembali":ab.kembali if ab.kembali is not None else "-",
                    "pulang":ab.pulang if ab.pulang is not None else "-",
                    "masuk_b":ab.masuk_b if ab.masuk_b is not None else "-",
                    "istirahat_b":ab.istirahat_b if ab.istirahat_b is not None else "-",
                    "kembali_b":ab.kembali_b if ab.kembali_b is not None else "-",
                    "pulang_b":ab.pulang_b if ab.pulang_b is not None else "-"
                }
                data.append(obj)
            # print(data)
        return JsonResponse({"status":'success',"msg":"berhasil mengambil data","data":data})
            
    
    
@login_required
def tketerangan_json(r,sid):
    if r.headers["X-Requested_With"] == "XMLHttpRequest":
        tgl1 = r.POST.get("tgl1")
        tgl2 = r.POST.get("tgl2")
        print(tgl2,tgl1 == '',"LIHAT")
        if (tgl1 == "" and tgl2 == "") or (tgl1 is None and tgl2 is None):
            tgl2 = datetime.now()
            tgl1 = tgl2 - timedelta(days=1)
        else:
            tgl2 = datetime.strptime(tgl2,'%d-%m-%Y').date()
            tgl1 = datetime.strptime(tgl1,'%d-%m-%Y').date()
        hari = datetime.now().strftime("%A")
        hari = nama_hari(hari)
        data = []
        id_user = r.user.id
        div = [d.divisi for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)]
        if sid == 0:
            result = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__hari_off","pegawai__hari_off2","pegawai","pegawai__divisi").filter(~Q(pegawai__hari_off__hari=hari) | ~Q(pegawai__hari_off2__hari=hari) ,tgl_absen__range=[tgl1,tgl2],pegawai__divisi__in=div)
        else:
            result = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__hari_off","pegawai__hari_off2","pegawai","pegawai__divisi").filter(~Q(pegawai__hari_off__hari=hari) | ~Q(pegawai__hari_off2__hari=hari) ,tgl_absen__range=[tgl1,tgl2],pegawai__status_id=int(sid),pegawai__divisi__in=div)
        for ab in result:
            if (ab.masuk is not None or ab.pulang is not None) or (ab.masuk_b is not None or ab.pulang_b is not None ):
                pass
            else:
                if ab.keterangan_absensi is not None or ab.keterangan_ijin is not None or ab.keterangan_lain is not None:
                    pass
                else:
                    obj = {
                        "id":ab.pk,
                        "tanggal":ab.tgl_absen,
                        "pegawai":ab.pegawai.nama,
                        "nik":ab.pegawai.nik,
                        "shift":ab.pegawai.shift,
                        "divisi":ab.pegawai.divisi.divisi,
                        "masuk":ab.masuk,
                        "istirahat":ab.istirahat,
                        "kembali":ab.kembali,
                        "pulang":ab.pulang,
                        "masuk_b":ab.masuk_b,
                        "istirahat_b":ab.istirahat_b,
                        "kembali_b":ab.kembali_b,
                        "pulang_b":ab.pulang_b,
                        "jam_masuk":ab.jam_masuk
                    }
                    data.append(obj)
            # print(data)
        return JsonResponse({"status":'success',"msg":"berhasil mengambil data","data":data})
            
            
    
    
@login_required
def terlambat_json(r,sid):
    if r.headers["X-Requested_With"] == "XMLHttpRequest":
        tgl1 = r.POST.get("tgl1")
        tgl2 = r.POST.get("tgl2")
        print(tgl2,tgl1 == '',"LIHAT")
        if (tgl1 == "" and tgl2 == "") or (tgl1 is None and tgl2 is None):
            tgl2 = datetime.now()
            tgl1 = tgl2 - timedelta(days=1)
        else:
            tgl2 = datetime.strptime(tgl2,'%d-%m-%Y').date()
            tgl1 = datetime.strptime(tgl1,'%d-%m-%Y').date()
        hari = datetime.now().strftime("%A")
        hari = nama_hari(hari)
        data = []
        id_user = r.user.id
        div = [d.divisi for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)]
        
        if sid == 0:
            result = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__hari_off","pegawai__hari_off2","pegawai","pegawai__divisi").filter(~Q(pegawai__hari_off__hari=hari) | ~Q(pegawai__hari_off2__hari=hari) ,tgl_absen__range=[tgl1,tgl2],pegawai__divisi__in=div)
        else:
            result = absensi_db.objects.using(r.session["ccabang"]).select_related("pegawai__hari_off","pegawai__hari_off2","pegawai","pegawai__divisi").filter(~Q(pegawai__hari_off__hari=hari) | ~Q(pegawai__hari_off2__hari=hari) ,tgl_absen__range=[tgl1,tgl2],pegawai__status_id=int(sid),pegawai__divisi__in=div)
        for ab in result:
            if (ab.masuk is not None or ab.pulang is not None) or (ab.masuk_b is not None or ab.pulang_b is not None ):
                if ab.jam_masuk is not None and ab.masuk is not None:
                    if ab.masuk > ab.jam_masuk:
                        obj = {
                            "id":ab.pk,
                            "tanggal":ab.tgl_absen,
                            "pegawai":ab.pegawai.nama,
                            "nik":ab.pegawai.nik,
                            "shift":ab.pegawai.shift,
                            "divisi":ab.pegawai.divisi.divisi,
                            "masuk":ab.masuk if ab.masuk is not None else "-",
                            "istirahat":ab.istirahat if ab.istirahat is not None else "-",
                            "kembali":ab.kembali if ab.kembali is not None else "-",
                            "pulang":ab.pulang if ab.pulang is not None else "-",
                            "masuk_b":ab.masuk_b if ab.masuk_b is not None else "-",
                            "istirahat_b":ab.istirahat_b if ab.istirahat_b is not None else "-",
                            "kembali_b":ab.kembali_b if ab.kembali_b is not None else "-",
                            "pulang_b":ab.pulang_b if ab.pulang_b is not None else "-",
                            "jam_masuk":ab.jam_masuk
                        }
                        data.append(obj)
                    else:
                        continue
            # print(data)
        return JsonResponse({"status":'success',"msg":"berhasil mengambil data","data":data})
            