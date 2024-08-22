from hrd_app.controllers.lib import *

@login_required
def laporan(r,sid):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dr = datetime.strptime("2015","%Y")
        sp = datetime.today()
        list_year = []
        for i in range(dr.year,sp.year+1):
            list_year.append(i)
        dsid = dakses.sid_id     
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        ###
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0
        jenis_ijin = jenis_ijin_db.objects.all()   
        data = {
            'akses' : akses,
            'status' : status,
            'dsid': dsid,
            'sid': sid,
            'sil': sid_lembur,
            'jenis_ijin' : jenis_ijin,
            "list_year":list_year,
            "bulan":sp.month,
            "tahun":sp.year,
            'modul_aktif' : 'Laporan'
        }
        
        return render(r,'hrd_app/laporan/laporan.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    

def laporan_json(r):
    sid = r.POST.get('sid')
    bulan = r.POST.get('bulan')
    tahun = r.POST.get('tahun')
    date = tahun+"-"+bulan+"-25"
    sp = datetime.today().strftime(date)
    sp = datetime.strptime(sp, '%Y-%m-%d')
    dr = sp - timedelta(days=30)
    print(dr,sp)

    data = []

    if int(sid) == 0:
        pegawai = pegawai_db.objects.all()
        for pgw in pegawai:
            off = 0
            terlambat = 0
            terlambat_ijin = 0
            total_hari = 0
            ab = absensi_db.objects.filter(pegawai_id = pgw.id, tgl_absen__range=[dr,sp])
            if ab.exists():
                for a in ab:
                    if a.keterangan_absensi == "OFF":
                        off += 1
                    if a.masuk is not None and a.pulang is not None:
                        total_hari += 1
                    if a.jam_masuk is not None and a.masuk is not None:
                        if a.masuk > a.jam_masuk:
                            if a.keterangan_ijin is not None:
                                terlambat_ijin += 1
                            else:
                                terlambat += 1
            obj = {
                "id" : pgw.id,
                "nik":pgw.nik,
                "jk":pgw.gender[0],
                "nama": pgw.nama,
                "divisi":pgw.divisi.divisi,
                "off": off,
                "terlambat": terlambat,
                "hari_off":pgw.hari_off.hari,
                "terlambat_ijin": terlambat_ijin,
                "total_hari": total_hari,
            }
            data.append(obj)
    else:
        pegawai = pegawai_db.objects.filter(status_id = sid)
        for pgw in pegawai:
            off = 0
            terlambat = 0
            terlambat_ijin = 0
            total_hari = 0
            ab = absensi_db.objects.filter(pegawai_id = pgw.id, tgl_absen__range=[dr,sp])
            if ab.exists():
                for a in ab:
                    if a.keterangan_absensi == "OFF":
                        off += 1
                    if a.masuk is not None and a.pulang is not None:
                        total_hari += 1
                    if a.jam_masuk is not None and a.masuk is not None:
                        if a.masuk > a.jam_masuk:
                            if a.keterangan_ijin is not None:
                                terlambat_ijin += 1
                            else:
                                terlambat += 1
            obj = {
                "id" : pgw.id,
                "nik":pgw.nik,
                "jk":pgw.gender[0],
                "nama": pgw.nama,
                "divisi":pgw.divisi.divisi,
                "off": off,
                "terlambat": terlambat,
                "hari_off":pgw.hari_off.hari,
                "terlambat_ijin": terlambat_ijin,
                "total_hari": total_hari,
            }
            data.append(obj)
    for dt in data:
        print(dt,"\n") 
    return JsonResponse({"data":data},status=200)



def laporan_json_periode(r,sid,periode):
    pass