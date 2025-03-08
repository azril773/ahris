from ..lib import *

def trxabsen_non(r):
    try:
        hari = r.POST.get("hari")
        hr = int(hari)
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(status="Active")
        absen = []
        today = datetime.today()
        userids = []
        data = []
        for m in mesin:
            zk = ZK(m.ipaddress,4370,60)
            print("OKOKO")
            try:
                conn = zk.connect()
                conn.disable_device()   
                for ab in conn.get_attendance():
                    kode = str(today - ab.timestamp).split(" ")
                    if len(kode) > 1:
                        if int(kode[0]) <= hr and ab.user_id not in userids:
                            userids.append(ab.user_id)
                        else:
                            pass
                    else:
                        pass
                conn.enable_device()
                conn.disconnect()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(type(e))
                if type(e) == exception.ZKNetworkError or type(e) == exception.ZKError or type(e) == exception.ZKErrorConnection or type(e) == exception.ZKErrorResponse:
                    raise Exception(f"Terjadi kesalahan pada mesin {m.nama} - {m.ipaddress}")
                else:
                    raise Exception("Terjadi kesalahan")
        for msn in mesin:
            zk1 = ZK(msn.ipaddress,4370,60)
            try:
                conn1 = zk1.connect()
                conn1.disable_device()   
                userid = [u.user_id for u in conn1.get_users()]
                absen = conn1.get_attendance()
                for id in userid:
                    if id not in userids:
                        data.append({"userid":id,"mesin":msn.nama})
                conn1.enable_device()
                conn1.disconnect()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(type(e))
                if type(e) == exception.ZKNetworkError or type(e) == exception.ZKError or type(e) == exception.ZKErrorConnection or type(e) == exception.ZKErrorResponse:
                    raise Exception(f"Terjadi kesalahan pada mesin {msn.nama} - {msn.ipaddress}")
                else:
                    raise Exception("Terjadi kesalahan")
        # print(absen)    
        print(data)
        return JsonResponse({"status":"success","msg":"Berhasil mengambil data absensi","data":data},status=200)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if len(e.args) > 0 else "Terjadi kesalahan"
        return JsonResponse({"status":"error","msg":msg},status=400)
    

def trxabsen_json(r):
    mesin = r.POST.getlist("mesin[]")
    dari = r.POST.get("dari")
    sampai = r.POST.get("sampai")
    if not mesin or not dari or not sampai:
        return JsonResponse({"status":"error","msg":"Harap isi form dengan lengkap"},status=400)
    try:
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(id__in=mesin)
        pegawai = [p for p in pegawai_db.objects.using(r.session['ccabang']).all().values("id","nama","userid")]
        pegawai_arsip = [pa for pa in pegawai_db_arsip.objects.using(r.session['ccabang']).all().values("id","nama","userid")]
        pegawais = pegawai + pegawai_arsip
        absen = []
        dr = datetime.strptime(dari+" 00:00:00","%d-%m-%Y %H:%M:%S")
        sp = datetime.strptime(sampai+" 23:59:59","%d-%m-%Y %H:%M:%S")
        for m in mesin:
            zk = ZK(m.ipaddress,4370,60)
            try:
                conn = zk.connect()
                conn.disable_device()
                for ab in conn.get_attendance():
                    if dr <= ab.timestamp <= sp:
                        pg = next((pgw for pgw in pegawais if str(pgw["userid"]).strip() == str(ab.user_id).strip()),None)
                        nama = pg["nama"] if pg is not None else '-'
                        absen.append({
                            "userid":ab.user_id,
                            "jam_absen":datetime.strftime(ab.timestamp,"%Y-%m-%d %H:%M:%S"),
                            "nama":nama,
                            'userid':ab.user_id,
                            "punch":ab.punch,
                            "mesin":m.nama
                        })
                conn.enable_device()
                conn.disconnect()
            except Exception as e:
                conn.enable_device()
                conn.disconnect()
                raise e
        data = sorted(absen, key=lambda i: i['jam_absen'],reverse=True)
        return JsonResponse({'status':"success","msg":"Berhasil ambil data mesin",'data':data},status=200)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if len(e.args) > 0 else "Terjadi kesalahan"
        return JsonResponse({"status":'error',"msg":msg},status=400)

def filtertrx(r):
    try:
        userids = r.POST.get("userid")
        idmesin = r.POST.getlist("mesin[]")
        dari = r.POST.get("dari")
        sampai = r.POST.get("sampai")
        if not userids or not idmesin or not dari or not sampai:
            return JsonResponse({"status":'error',"msg":"Harap isi form dengan lengkap"},status=400)

        dr = datetime.strptime(dari+" 00:00:00","%d-%m-%Y %H:%M:%S")
        sp = datetime.strptime(sampai+" 23:59:59","%d-%m-%Y %H:%M:%S")
        pegawai = [p for p in pegawai_db.objects.using(r.session['ccabang']).all().values("id","nama","userid")]
        pegawai_arsip = [pa for pa in pegawai_db_arsip.objects.using(r.session['ccabang']).all().values("id","nama","userid")]
        pegawais = pegawai + pegawai_arsip
        mesin = mesin_db.objects.using(r.session["ccabang"]).filter(id__in=idmesin)
        absen = []
        userid = [str(u).strip() for u in userids.split(",")]
        for m in mesin:
            zk = ZK(m.ipaddress,4370,60)
            try:
                conn = zk.connect()
                conn.disable_device()
                for ab in conn.get_attendance():
                    if dr <= ab.timestamp <= sp:
                        if str(ab.user_id).strip() in userid:
                            pg = next((pgw for pgw in pegawais if str(pgw["userid"]).strip() == str(ab.user_id).strip()),None)
                            nama = pg["nama"] if pg is not None else '-'
                            absen.append({
                                "userid":ab.user_id,
                                "jam_absen":datetime.strftime(ab.timestamp,"%Y-%m-%d %H:%M:%S"),
                                "nama":nama,
                                'userid':ab.user_id,
                                "punch":ab.punch,
                                "mesin":m.nama
                            })
                conn.enable_device()
                conn.disconnect()
            except Exception as e:
                print(e)
                if type(e) == exception.ZKErrorResponse():
                    conn.enable_device()
                    conn.disconnect()
                raise e
        # print(absen)    
        data = sorted(absen, key=lambda i: i['jam_absen'],reverse=True)
        return JsonResponse({"status":"success","msg":"Berhasil mengambil data absensi","data":data },status=200)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        msg = e.args[0] if len(e.args) > 0 else "Terjadi kesalahan"
        return JsonResponse({"status":"error","msg":msg},status=400)

authorization(["root"])
def trxabsen(r):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    mesin = mesin_db.objects.using(r.session['ccabang']).all()
    data = {
        "sid":akses.sid_id,
        "dsid":akses.sid_id,
        "mesin":mesin
    }
    return render(r,"hrd_app/trxabsen/trxabsen.html",data)

# def sinkrontrans(r):
#     pegawai = pegawai_db.objects.using(r.session['ccabang']).all().values("id","nama",'userid')
#     for pg in pegawai_db.objects.using('tasiklm').all():
#         pgw = next((p for p in pegawai if p["id"] == pg.pk),None)
#         if not pgw:
#             continue
#         data_raw_db.objects.using(r.session["ccabang"]).filter(userid=pg.userid).update(userid=pgw["userid"])
