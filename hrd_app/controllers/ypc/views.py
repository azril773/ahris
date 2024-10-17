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