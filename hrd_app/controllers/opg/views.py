from hrd_app.controllers.lib import *
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# OPG
@authorization(["*"])
def opg(r, sid):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_skrg()
        dari = datetime.strptime(pa[0].date().strftime("%d-%m-%Y"),"%d-%m-%Y").date()
        sampai = datetime.strptime(pa[1].date().strftime("%d-%m-%Y"),"%d-%m-%Y").date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')                 
        
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
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").filter(aktif=1,divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
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
            'modul_aktif' : 'OPG'
        }
        
        return render(r,'hrd_app/opg/[sid]/opg.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def cari_opg(r):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dr = r.POST.get('ctgl1')
        sp = r.POST.get('ctgl2')
        sid = r.POST.get('sid')
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'OPG'
        }
        
        return render(r,'hrd_app/opg/copg/[dr]/[sp]/[sid]/copg.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def cari_opg_sid(r, dr, sp, sid):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()               
        
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.using(r.session["ccabang"]).get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else:
                if int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
                else:
                    pass    
                        
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'status' : status,
            'pegawai' : pegawai,
            'dsid' : dsid,
            'sid' : int(sid),
            'sil': sid_lembur,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'OPG'
        }
        
        return render(r,'hrd_app/opg/copg/[dr]/[sp]/[sid]/copg.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def opg_json(r, dr, sp, sid):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        if int(sid) == 0:
            for i in opg_db.objects.using(r.session["ccabang"]).select_related("pegawai","pegawai__divisi").filter(opg_tgl__range=(dari,sampai),pegawai__divisi_id__in=aksesdivisi):
                
                if i.diambil_tgl is not None:
                    dtgl = datetime.strftime(i.diambil_tgl, '%d-%m-%Y')
                else:
                    dtgl = None    
                            
                op = {
                    'id':i.id,
                    'opg_tgl':datetime.strftime(i.opg_tgl, '%d-%m-%Y'),
                    'diambil_tgl':dtgl,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan,
                    'status':i.status
                }
                data.append(op)
        else:
            for i in opg_db.objects.using(r.session["ccabang"]).select_related("pegawai","pegawai__divisi").filter(opg_tgl__range=(dari,sampai), pegawai__status_id=int(sid),pegawai__divisi_id__in=aksesdivisi):
                
                if i.diambil_tgl is not None:
                    dtgl = datetime.strftime(i.diambil_tgl, '%d-%m-%Y')
                else:
                    dtgl = None 
                            
                op = {
                    'id':i.id,
                    'opg_tgl':datetime.strftime(i.opg_tgl, '%d-%m-%Y'),
                    'diambil_tgl':dtgl,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ket':i.keterangan,
                    'status':i.status
                }
                data.append(op)
        return JsonResponse({"data": data})


@authorization(["*"])
def tambah_opg(r):
    nama_user = r.session["user"]["nama"]
    
    dtgl = r.POST.get('tgl')
    dpegawai = r.POST.get('pegawai')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
    tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()   
    try:
        pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=int(dpegawai),divisi_id__in=aksesdivisi)  
    except:
        return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
    off = pg.hari_off.hari
    
    if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur=tgl).exists():
        ln = libur_nasional_db.objects.using(r.session["ccabang"]).get(tgl_libur=tgl)
        tln = ln.tgl_libur
    else:
        tln = None    
    
    day = tgl.strftime("%A")
    nh = nama_hari(day) 
            
    if opg_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").filter(pegawai_id=int(dpegawai), opg_tgl=tgl,pegawai__divisi_id__in=aksesdivisi).exists():
        status = 'duplikat'
    else:        
        
        # cek jika sudah terdapat opg, batalkan
        if geseroff_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(dpegawai), dari_tgl=tgl).exists():
            status = 'ada geseroff'
        else:
            # cek jika absen di tanggal opg tgl tidak ada absen masuk atau absen pulangnya, batalkan
            # if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=tgl).exists():
                
            #     ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=tgl)

            #     if ab.masuk is None and ab.pulang is None:
            #         status = 'pegawai tidak masuk'
            #     else:
            if nh == off:
                topg = opg_db(
                    
                    pegawai_id = int(dpegawai),
                    opg_tgl = tgl,
                    keterangan = 'OFF Pengganti Reguler',
                    add_by = nama_user,
                    edit_by = nama_user
                )
                topg.save(using=r.session["ccabang"])
                
                status = 'ok'
            else:
                if tln is not None:
                    if tln == tgl:
                        topg = opg_db(
                            pegawai_id = int(dpegawai),
                            opg_tgl = tgl,
                            keterangan = 'OFF Pengganti Tgl Merah',
                            add_by = nama_user,
                            edit_by = nama_user
                        )
                        topg.save(using=r.session["ccabang"])
                
                        status = 'ok'
                    else:
                        status = 'bukan tgl merah'
                else:
                    status = 'bukan off reguler'   
                                    
    return JsonResponse({"status": status})


@authorization(["*"])
def pakai_opg(r):
    nama_user = r.session["user"]["nama"]
    
    idopg = r.POST.get('id_pakai')
    dtgl = r.POST.get('ptgl')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
    
    diambil_tgl = datetime.strptime(dtgl,'%d-%m-%Y').date()
    try:
        opg = opg_db.objects.using(r.session["ccabang"]).select_related("pegawai__divisi").get(id=int(idopg),pegawai__divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":"error","msg":"Opg tidak ada"},status=400)
    idp = opg.pegawai_id
    opg_tgl = datetime.strftime(opg.opg_tgl,'%d-%m-%Y')
    
    try:
        pg = pegawai_db.objects.using(r.session["ccabang"]).select_related("divisi").get(id=int(idp),divisi_id__in=aksesdivisi)  
    except:
        return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
    off = pg.hari_off.hari
    day = diambil_tgl.strftime("%A")
    nh = nama_hari(day) 
            
    if absensi_db.objects.using(r.session["ccabang"]).filter(tgl_absen=diambil_tgl, pegawai_id=int(idp)).exists():
        
        ab = absensi_db.objects.using(r.session["ccabang"]).get(tgl_absen=diambil_tgl, pegawai_id=int(idp))
        
        if ab.masuk is None and ab.pulang is None:
            if off == nh:
                status = 'hari off'
            else:
                if geseroff_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), ke_tgl=diambil_tgl).exists():
                    status = 'ada geseroff'
                else:        
                    
                    if diambil_tgl < datetime.strptime(opg_tgl,"%d-%m-%Y").date():
                        return JsonResponse({"status":"error","msg":"'diambil tanggal' harus lebih besar dari tanggal opg. Silahkan gunakan geser off"},status=400)
                    ab.keterangan_absensi = f"OPG-({opg_tgl})"
                    ab.save(using=r.session["ccabang"])
                    
                    opg.diambil_tgl = diambil_tgl
                    opg.status = 1
                    opg.edit_by = nama_user
                    opg.save(using=r.session["ccabang"])
                    
                    status = 'ok'
        else:
            status = 'pegawai masuk'    
    else:
        if diambil_tgl < datetime.strptime(opg_tgl,"%d-%m-%Y").date():
            return JsonResponse({"status":"error","msg":"'diambil tanggal' harus lebih besar dari tanggal opg. Silahkan gunakan geser off"},status=400)
        opg.status = 1
        opg.diambil_tgl = diambil_tgl
        opg.edit_by = nama_user
        opg.save(using=r.session["ccabang"])
        status = 'ok'
        # status = "data absensi tidak ada"     
    return JsonResponse({"status": status})


@authorization(["*"])
def batal_opg(r):
    nama_user = r.session["user"]["nama"]
    
    idopg = r.POST.get('id_batal')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
    try:
        opg = opg_db.objects.using(r.session["ccabang"]).select_related('pegawai','pegawai__divisi').get(id=int(idopg),pegawai__divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":"error","msg":"Opg tidak ada"},status=400)
    idp = opg.pegawai_id
    tgl = opg.diambil_tgl
    
    ab = absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), tgl_absen=tgl).last()
    if ab is not None:
        ab.keterangan_absensi = None
        ab.save(using=r.session["ccabang"])
    
    opg.diambil_tgl = None
    opg.status = 0
    opg.edit_by = nama_user
    opg.save(using=r.session["ccabang"])
    
    status = 'ok'
                                  
    return JsonResponse({"status": status})


@authorization(["*"])
def hapus_opg(r):
    nama_user = r.session["user"]["nama"]
    
    idopg = r.POST.get('id_hapus')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
    try:
        opg = opg_db.objects.using(r.session["ccabang"]).select_related('pegawai',"pegawai__divisi").get(id=int(idopg),pegawai__divisi_id__in=aksesdivisi)
    except:
        return JsonResponse({"status":'error',"msg":"Opg tidak ada"},status=400)
    idp = opg.pegawai_id
    nama_pegawai = opg.pegawai.nama
    tgl_ambil = opg.diambil_tgl
    tgl_opg = opg.opg_tgl
    
    if opg.status == 1:
        try:
            ab = absensi_db.objects.using(r.session["ccabang"]).get(pegawai_id=int(idp), tgl_absen=tgl_ambil)
        except:
            return JsonResponse({"status":'error',"msg":"Tidak ada absensi"},status=400)
        ab.keterangan_absensi = None
        ab.save(using=r.session["ccabang"])       
    else:
        pass
    
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"OPG-(a.n {nama_pegawai}, tgl:{tgl_opg})"
    )
    histori.save(using=r.session["ccabang"])    
    
    opg.delete(using=r.session["ccabang"])
        
    status = 'ok'
                                  
    return JsonResponse({"status": status})


def readcuti(r):
    with open("static/absensi_chd.json","rb") as f:
        data = json.loads(f.read())
        # pegawai_db.objects.using(r.session["ccabang"]).bulk_update([pegawai_db(id=dt["id"],tgl_masuk=datetime.strptime(dt["tgl_aktif"],"%Y-%m-%d %H:%M:%S").date()) for dt in data["data"]],["tgl_masuk"])
        # idstr = ''
        # for dt in data["data"]:
        #     idstr += str(dt["id"])+","
        # print(idstr)
        # for m in ["15.63.254.204","15.63.254.210","15.63.254.209","15.63.254.207",'15.63.254.207',"15.63.254.206",'15.63.254.211']:
        #     zk = ZK(m, port=4370, timeout=60)
        #     conn = zk.connect()
        #     conn.disable_device()

        # datas = ''
        patterjenis = ""
        for j in jenis_ijin_db.objects.using(r.session["ccabang"]).all():
            if re.search('opg|geser off|cuti|alfa',j.jenis_ijin,re.IGNORECASE) is not None:
                continue
            patterjenis += j.jenis_ijin +"|"
        pattern = patterjenis.strip().split("|")
        pattern.pop()
        patternjoin = "|".join(pattern)
        for dt in data["data"]:
            if dt["jam_absen_masuk"] is not None:
                dt["jam_absen_masuk"] = dt["jam_absen_masuk"].split(" ")[1]
            if dt["jam_absen_keluar"] is not None:
                dt["jam_absen_keluar"] = dt["jam_absen_keluar"].split(" ")[1]
            if dt["jam_absen_kembali"] is not None:
                dt["jam_absen_kembali"] = dt["jam_absen_kembali"].split(" ")[1]
            if dt["jam_absen_pulang"] is not None:
                dt["jam_absen_pulang"] = dt["jam_absen_pulang"].split(" ")[1]
            if dt["jam_absen_masuk2"] is not None:
                dt["jam_absen_masuk2"] = dt["jam_absen_masuk2"].split(" ")[1]
            if dt["jam_absen_keluar2"] is not None:
                dt["jam_absen_keluar2"] = dt["jam_absen_keluar2"].split(" ")[1]
            if dt["jam_absen_kembali2"] is not None:
                dt["jam_absen_kembali2"] = dt["jam_absen_kembali2"].split(" ")[1]
            if dt["jam_absen_pulang2"] is not None:
                dt["jam_absen_pulang2"] = dt["jam_absen_pulang2"].split(" ")[1]
            dt["keterangan_ijin"] = None
            dt["keterangan_lain"] = None
            dt["keterangan_absensi"] = None
            if dt["keterangan"] is not None:
                if re.search(patternjoin,dt["keterangan"],re.IGNORECASE) is not None:
                    dt["keterangan_ijin"] = dt["keterangan"]
                elif re.search("kompensasi",dt["keterangan"],re.IGNORECASE) is not None:
                    dt["keterangan_lain"] = dt["keterangan"]
                else:
                    dt["keterangan_absensi"] = dt["keterangan"]
            elif dt["ubah_keterangan"] is not None:
                if re.search(patternjoin,dt["ubah_keterangan"],re.IGNORECASE) is not None:
                    dt["keterangan_ijin"] = dt["ubah_keterangan"]
                elif re.search("kompensasi",dt["ubah_keterangan"],re.IGNORECASE) is not None:
                    dt["keterangan_lain"] = dt["ubah_keterangan"]
                else:
                    dt["keterangan_absensi"] = dt["ubah_keterangan"]
            del dt["keterangan"]
            del dt["ubah_keterangan"]
            
                    
        absensi_db.objects.using(r.session['ccabang']).bulk_create([absensi_db(tgl_absen=d["tgl_absen"],masuk=d["jam_absen_masuk"],istirahat=d["jam_absen_keluar"],kembali=d["jam_absen_kembali"],istirahat2=d["jam_absen_keluar2"],kembali2=d["jam_absen_kembali2"],pulang=d["jam_absen_pulang"],keterangan_absensi=d["keterangan_absensi"],keterangan_ijin=d["keterangan_ijin"],keterangan_lain=d["keterangan_lain"],libur_nasional=d["libur_nasional"],insentif=d["j_insentif"],jam_masuk=d["jadwal_masuk"],lama_istirahat=d["jadwal_ist"],jam_pulang=d["jadwal_pulang"],total_jam_kerja=d["lama_kerja"],total_jam_istirahat=d["lama_istirahat"],total_jam_istirahat2=d["lama_istirahat2"],lebih_jam_kerja=d["tplus"],pegawai_id=d["pegawai_id"]) for d in data["data"]],batch_size=3000)

        # for dt in data["data"]:
        #     keterangan = dt["keterangan"]

        #     cuti_ke = re.findall('\d{1,2}',keterangan)
        #     dt["cuti_ke"] = cuti_ke[0]
        #     dt["keterangan"] = "Cuti ke "+cuti_ke[0]+"-()"

        # cuti_db.objects.using(r.session["ccabang"]).bulk_create([cuti_db(pegawai_id=int(d["pegawai_id"]),tgl_cuti=d["tgl_ijin"],cuti_ke=int(d["cuti_ke"]),keterangan=d["keterangan"],add_by=d["add_by"],edit_by=d["edit_by"],add_date=d["add_date"],edit_date=d["edit_date"]) for d in data["data"]]) 
        # pegawai_db.objects.using(r.session["ccabang"]).bulk_update([pegawai_db(id=dt["id"],sisa_cuti=dt["cuti"]) for dt in data["data"]],["sisa_cuti"])
        # userids = ["201004","201005","201006","201021","201052","201057","201071","201090","201099","202011","202015","202022","202028","207003","207009","207012","207013","207014","207016","207017","207018","207031","209004","209008","209009","209010","209012","209013","209016","209021","209022","209024","209025","209027","209030","209032","209033","209035","209040","209041","209042","209044","209045","209047","209049","209050","209052","209053","209056","209061","209062","209064","209065","209066","209067","209068","209071","209072","209081","209089","209090","209092","209093","209097","209098","209100","209102","209103","209106","209107","209108","209112","209117","209118","209120","209121","209122","209124","209126","209128","209132","209133","209134","210002","210003","210008","210010","210011","210014","210015","210016","210018","210022","210023","210024","210025","210028","210032","210035","210036","210038","210039","210044","210046","210048","210050","210059","210061","210062","210063","210065","210066","210068","210072","210073","210077","210078","210079","210080","210082","210083","210085","210086","214001","216001","216005","216010","216011","216017","216019","216022","216024","216026","216029","216031","218026","218035","218044","218050","218065","218066","218067","218078","218079","218083","218087","218093","218098","218100","218101","218114","218115","218116","218119","218128","218130","218132","218133","218135","218137","218140","218145","218148","218149","218153","218154","218158","218160","218172","218174","218176","218177","218178","218179","218181","218182","218186","218190","218191","218196","218199","218203","218208","218211","218215","218217","218225","218228","218229","218231","218233","218237","218241","218244","218248","218250","218252","218254","218256","218257","218263","218279","218280","219013","219024","219025","219027","219031","219042","219044","219048","219054","219059","219063","219066","219077","220008","220053","220073","220074","220147","220152","220154","220163","221005","221028","221040","221046","221055","221072","221075","221216","221217","221218","221219","221220","221221","221223","221224","221233","221236","221237","221240","221241","221243","221244","221245","221254","221257","221258","221259","221260","221263","221288","221290","221291","221292","221293","221294","221295","221300","221306","221307","221308","222009","222018","222019","222031","222035","222045","222082","222099","222132","222138","222143","222144","222145","222153","222162","222180","222212","222242","222250","222261","222264","222268","222278","222279","222282","222286","222288","222292","222295","222298","222302","222303","222304","222305","222306","222307","222308","222317","222318","222322","222324","222333","222334","222335","222336","222337","222338","222339","222340","222341","222342","222343","222344","222345","222357","222358","222364","222365","222370","222376","222377","222378","222382","222383","222388","222392","222394","222396","222400","222406","222409","222410","222411","222420","222424","222425","222427","222430","222431","222433","222438","222439","222442","222443","222446","222447","222452","222454","222460","222461","222465","222467","222468","222469","222470","222474","222477","222478","222479","222482","222483","222484","222486","222487","222490","222492","222496","222498","222500","223003","223006","5249","5800"]
        # dataraw = data_raw_db.objects.using(r.session['ccabang']).filter(userid__in=userids,jam_absen__range=['2025-03-23 00:00:00','2025-03-23 00:30:00'],punch=1).distinct("userid")
        # print(len(dataraw))
        # for raw in dataraw:
        #     # print(raw.jam_absen).
        #     absensi_db.objects.using(r.session['ccabang']).filter(pegawai__userid=raw.userid,tgl_absen='2025-03-22').update(pulang=raw.jam_absen.time())
        # data_trans_db.objects.using(r.session["ccabang"]).bulk_create([data_trans_db(userid=raw.userid,jam_absen='2025-03-22 '+str(raw.jam_absen.time()),punch=7,mesin=raw.mesin,keterangan="Pulang Malam") for raw in dataraw])
        # hari = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
        # create = []
        # for j in jamkerja_db.objects.using(r.session["ccabang"]).all():
        #     if j.hari == "All":
        #         for i in range(0,7):
        #             create.append(jamkerja_db(kk_id=j.kk_id,jam_masuk=j.jam_masuk,jam_pulang=j.jam_pulang,lama_istirahat=j.lama_istirahat,hari=hari[i],add_by=j.add_by,edit_by=j.edit_by,add_date=j.add_date,edit_date=j.edit_date,shift_id=1))
        #         j.delete(using=r.session["ccabang"])
        #     elif j.hari == 'Biasa':
        #         for i in range(0,5):
        #             create.append(jamkerja_db(kk_id=j.kk_id,jam_masuk=j.jam_masuk,jam_pulang=j.jam_pulang,lama_istirahat=j.lama_istirahat,hari=hari[i],add_by=j.add_by,edit_by=j.edit_by,add_date=j.add_date,edit_date=j.edit_date,shift_id=1))
        #         j.delete(using=r.session["ccabang"])
        #     else:
        #         continue
        # jamkerja_db.objects.using(r.session["ccabang"]).bulk_create(create)
        

