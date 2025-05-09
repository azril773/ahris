
from hrd_app.controllers.lib import *
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ijin
@authorization(["*"])
def ijin(r, sid):
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
        
        sid_lembur = 0

        # 
        pegawai = []
        pp = []
            
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            elif int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)
            else:
                pass    
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(Q(gender__regex=r"(?i)perempuan") | Q(gender__regex=r"(?i)p"),divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pp.append(data)
            elif int(sid) == p.status_id:     
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pp.append(data)
            else:
                pass    
        ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).order_by('jenis_ijin')
                        
        data = {
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            'today' : today,
            'status' : status,
            'pegawai' : pegawai,
            "pp":pp,
            'dsid' : dsid,
            'sid' : sid,
            'sil': sid_lembur,
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(r,'hrd_app/ijin/[sid]/ijin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def cari_ijin(r):
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
        
        sid_lembur = 0

        pegawai = []
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1,divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else: 
                if p.status_id == int(sid):
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)   

        ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).order_by('jenis_ijin')
                        
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
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(r,'hrd_app/ijin/cijin/[dr]/[sp]/[sid]/cijin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def cari_ijin_sid(r, dr, sp, sid):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
                
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id')
        
        sid_lembur = 0

        pegawai = []
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=iduser)]
        for p in pegawai_db.objects.using(r.session["ccabang"]).filter(aktif=1,divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                data = {
                    'idp':p.id,
                    'nama':p.nama,
                    'nik':p.nik,
                    'userid':p.userid
                }    
                pegawai.append(data)
            else: 
                if p.status_id == int(sid):
                    data = {
                        'idp':p.id,
                        'nama':p.nama,
                        'nik':p.nik,
                        'userid':p.userid
                    }    
                    pegawai.append(data)   

        ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).order_by('jenis_ijin')
                        
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
            'ijin' : ijin,
            'dari' : dari,
            'sampai' : sampai,
            'dr': dr,
            'sp': sp,
            'modul_aktif' : 'Ijin'
        }
        
        return render(r,'hrd_app/ijin/cijin/[dr]/[sp]/[sid]/cijin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
def ijin_json(r, dr, sp, sid):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
        for i in ijin_db.objects.using(r.session["ccabang"]).select_related('pegawai','ijin').filter(tgl_ijin__range=(dari,sampai),pegawai__divisi_id__in=aksesdivisi):
            if int(sid) == 0:
                
                tijin = i.tgl_ijin.strftime("%A")
                hari = nama_hari(tijin) 
                
                ijin = {
                    'id':i.id,
                    'tgl':datetime.strftime(i.tgl_ijin, '%d-%m-%Y'),
                    'hari':hari,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ijin_id':i.ijin_id,
                    'ijin':i.ijin.jenis_ijin,
                    'ket':i.keterangan
                }
                data.append(ijin)
            elif int(sid) == i.pegawai.status_id:
                tijin = i.tgl_ijin.strftime("%A")
                hari = nama_hari(tijin) 
                
                ijin = {
                    'id':i.id,
                    'tgl':datetime.strftime(i.tgl_ijin, '%d-%m-%Y'),
                    'hari':hari,
                    'idp':i.pegawai_id,
                    'nama':i.pegawai.nama,
                    'nik':i.pegawai.nik,
                    'userid':i.pegawai.userid,
                    'divisi':i.pegawai.divisi.divisi,
                    'ijin_id':i.ijin_id,
                    'ijin':i.ijin.jenis_ijin,
                    'ket':i.keterangan
                }
                data.append(ijin)
            else:
                pass
                
                                
        return JsonResponse({"data": data})


@authorization(["*"])
def tambah_ijin(r):
    nama_user = r.session["user"]["nama"]
    
    dtgl = r.POST.get('tgl')
    dpegawai = r.POST.get('pegawai')
    dijin = r.POST.get('ijin')
    dket = r.POST.get('ket')
    aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=r.session["user"]["id"])]
    try:
       ij = jenis_ijin_db.objects.using(r.session["ccabang"]).get(id=int(dijin))
    except: 
        return JsonResponse({"status":"error","msg":"Jenis ijin tidak ada"},status=400)
    ltgl = dtgl.split(', ')
    for t in ltgl:
        tgl = datetime.strptime(t,'%d-%m-%Y')        
              
        if ijin_db.objects.using(r.session["ccabang"]).select_related('pegawai','ijin').filter(pegawai_id=int(dpegawai), tgl_ijin=tgl.date()).exists():
            status = 'duplikat'
        else:
            if absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=tgl.date()).exists():
                ab = absensi_db.objects.using(r.session["ccabang"]).select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=tgl.date())
                ab.keterangan_ijin = f'{ij.jenis_ijin}-({dket})'
                ab.save(using=r.session["ccabang"])
            else:
                pass 
                
            ijin_db(
                ijin_id = int(dijin),
                tgl_ijin = tgl.date(),
                pegawai_id = int(dpegawai),
                keterangan = dket,        
                add_by = nama_user,
                edit_by = nama_user
            ).save(using=r.session["ccabang"])

            status = 'ok'    
    
    return JsonResponse({"status": status})


@authorization(["*"])
def batal_ijin(r):
    nama_user = r.session["user"]["nama"]

    id_ijin = r.POST.get('id')
    
    try:
        ij = ijin_db.objects.using(r.session["ccabang"]).select_related('pegawai','ijin').get(id=int(id_ijin))
    except Exception as e:
        return JsonResponse({"status":"error","msg":"Ijin tidak ada"},status=400)
    tgl = ij.tgl_ijin
    idp = ij.pegawai_id
    nama_pegawai = ij.pegawai.nama
    jenis_ijin = ij.ijin.jenis_ijin
    abc = absensi_db.objects.using(r.session["ccabang"]).filter(pegawai_id=int(idp), tgl_absen=tgl)
    if abc.exists():
        ab = absensi_db.objects.using(r.session["ccabang"]).get(pegawai_id=int(idp), tgl_absen=tgl)
        ab.keterangan_ijin = None
        ab.save(using=r.session["ccabang"])

    
    histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"{jenis_ijin}-(a.n {nama_pegawai}, tgl:{tgl})"
    ).save(using=r.session["ccabang"])
    
    ij.delete(using=r.session["ccabang"])
    
    status = 'ok'    
    
    return JsonResponse({"status": status})




# Jenis Ijin
# ++++++++++++++
@authorization(["*"])
def jenis_ijin(r):
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
            'modul_aktif' : 'Jenis Ijin'     
        }
        
        return render(r,'hrd_app/ijin/jenis_ijin.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@authorization(["*"])
def jenis_ijin_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        jenis_ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).all()
        
        data = []

        for j in jenis_ijin:
            obj = {
                "pk":j.pk,
                "jenis_ijin":j.jenis_ijin
            }
            data.append(obj)
        return JsonResponse({"data":data},safe=False,status=200)

@authorization(["*"])
def tjenis_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")

    if jenis_ijin_db.objects.using(r.session["ccabang"]).filter(jenis_ijin=jenis_ijin).exists():
        status="duplikat"
    else:
        jenis_ijin_db(
            jenis_ijin=jenis_ijin
        ).save(using=r.session["ccabang"])
        status = "ok"
    return JsonResponse({"status":status},safe=False,status=200)

@authorization(["*"])
def ejenis_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")
    id = r.POST.get("id") 
    if jenis_ijin_db.objects.using(r.session["ccabang"]).filter(~Q(id=int(id)),jenis_ijin=jenis_ijin).exists():
        status = "duplikat"
    else:
        jenis_ijin_db.objects.using(r.session["ccabang"]).filter(id=int(id)).update(jenis_ijin=jenis_ijin)
        status = "ok"
    return JsonResponse({"status":status},safe=False,status=200)

@authorization(["*"])
def hjenis_ijin(r):
    id = r.POST.get("id")
    jenis_ijin = r.POST.get("jenis_ijin")
    nama_user = r.session["user"]["nama"]
    try:
        jenis_ijin_db.objects.using(r.session["ccabang"]).get(pk=int(id)).delete(using=r.session["ccabang"])
        thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus jenis ijin : {jenis_ijin}'
        )
        thapus.save(using=r.session["ccabang"])
        status = 'Ok'
    except:
        status = "gagal menghapus" 
    return JsonResponse({"status":status},safe=False,status=200)


@authorization(["*"])
def tcuti_melahirkan(r):
    dr = r.POST.get("dari")
    sp = r.POST.get("sampai")
    pegawai = r.POST.get("pegawai")

    try:
        pgw = pegawai_db.objects.using(r.session["ccabang"]).get(pk=int(pegawai))
    except:
        return JsonResponse({"status":400,"msg":"data pegawai tidak ada"},status=400)
    dari = datetime.strptime(dr,'%d-%m-%Y').date()
    sampai = datetime.strptime(sp,"%d-%m-%Y").date()
    data = []
    if ijin_db.objects.using(r.session["ccabang"]).filter(tgl_ijin__range=(dari,sampai),pegawai_id=pgw.pk,ijin__jenis_ijin=r'CM$').exists():
        return JsonResponse({"status":400,"msg":"Cuti melahirkan sudah ada","data":[]},status=400)
    ijin = jenis_ijin_db.objects.using(r.session["ccabang"]).filter(jenis_ijin__iregex=r"CM")
    if not ijin.exists():
        return JsonResponse({"status":400,"msg":"Jenis ijin tidak ada","data":[]},status=400)
    for i in range((sampai - dari).days +1 ):
        obj = {
            "pegawai_id":pgw.pk,
            "ijin_id":ijin[0].pk,
            "tgl_ijin":dari + timedelta(days=i),
            "keterangan":f"Dispensasi - Cuti Melahirkan (CM)"
        }
        data.append(obj)
    ijin_db.objects.using(r.session["ccabang"]).bulk_create([ijin_db(**i) for i in data])
    return JsonResponse({"status":"ok"},status=200)
