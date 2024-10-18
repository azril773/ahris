from hrd_app.controllers.lib import *

@login_required
def tlengkap(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            # 'sid': sid,
            'sil': sid_lembur,
            # "pegawai":pegawai,
            'modul_aktif' : 'Laporan'
        }
        return render(r,"hrd_app/ypc/tlengkap.html",data)


@login_required
def tketerangan(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            # 'sid': sid,
            'sil': sid_lembur,
            # "pegawai":pegawai,
            'modul_aktif' : 'Laporan'
        }
        return render(r,"hrd_app/ypc/tketerangan.html",data)

@login_required
def terlambat(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            # 'sid': sid,
            'sil': sid_lembur,
            # "pegawai":pegawai,
            'modul_aktif' : 'Laporan'
        }
        return render(r,"hrd_app/ypc/terlambat.html",data)
    
    
@login_required
def tlengkap_json(r):
    if re.headers["X-Requested_With"] == "XMLHttpRequest":
        today = datetime.now()
        tmin = today - timedelta(days=1)
        
        data = []
        for ab in absensi_db.objects.filter(tgl_absen__range=[tmin,today]):
            if (ab.masuk is not None and ab.pulang is not None and ab.istirahat is not None and ab.kembali is not None) or (ab.masuk_b is not None and ab.pulang_b is not None and ab.istirahat_b is not None and ab.kembali_b is not None):
                pass
            else:
                obj = {
                    "tanggal":ab.tgl_absen,
                    "pegawai":ab.pegawai.nama,
                    "nik":ab.pegawai.nik,
                    "shift":ab.pegawai.shift,
                    "divisi":ab.pegawai.divisi,
                    "masuk":ab.masuk,
                    "istirahat":ab.istirahat,
                    "kembali":ab.kembali,
                    "pulang":ab.pulang,
                    "masuk_b":ab.masuk_b,
                    "istirahat_b":ab.istirahat_b,
                    "kembali_b":ab.kembali_b,
                    "pulang_b":ab.pulang_b
                }
                data.append(obj)
        return JsonResponse({"status":'success',"msg":"berhasil mengambil data","data":data})
            