
from hrd_app.controllers.lib import *
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ijin
@login_required
def ijin(request, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        today = date.today()
        pa = periode_absen(today.month,today.year)
        dari = pa[0].date()
        sampai = pa[1].date()
        
        dr = datetime.strftime(dari,'%d-%m-%Y')
        sp = datetime.strftime(sampai,'%d-%m-%Y')
        
        status = status_pegawai_db.objects.all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        # print(sid_lembur.id)
        pegawai = []
        pp = []
            
        for p in pegawai_db.objects.filter(aktif=1):
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
        for p in pegawai_db.objects.filter(Q(gender="perempuan") | Q(gender="p"),aktif=1):
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
        
        ijin = jenis_ijin_db.objects.order_by('jenis_ijin')
                        
        data = {
            'akses' : akses,
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
        
        return render(request,'hrd_app/ijin/[sid]/ijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_ijin(request):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dr = request.POST.get('ctgl1')
        sp = request.POST.get('ctgl2')
        sid = request.POST.get('sid')
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date() 
                
        status = status_pegawai_db.objects.all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
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

        ijin = jenis_ijin_db.objects.order_by('jenis_ijin')
                        
        data = {
            'akses' : akses,
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
        
        return render(request,'hrd_app/ijin/cijin/[dr]/[sp]/[sid]/cijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def cari_ijin_sid(request, dr, sp, sid):
    iduser = request.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
                
        status = status_pegawai_db.objects.all().order_by('id')
        
        try:
            sid_lembur = status_pegawai_lembur_db.objects.get(status_pegawai_id = sid)
            sid_lembur = sid_lembur.status_pegawai.pk
        except:
            sid_lembur = 0

        pegawai = []
            
        for p in pegawai_db.objects.filter(aktif=1):
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

        ijin = jenis_ijin_db.objects.order_by('jenis_ijin')
                        
        data = {
            'akses' : akses,
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
        
        return render(request,'hrd_app/ijin/cijin/[dr]/[sp]/[sid]/cijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def ijin_json(request, dr, sp, sid):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        
        dari = datetime.strptime(dr,'%d-%m-%Y').date()
        sampai = datetime.strptime(sp,'%d-%m-%Y').date()
        print(sid,"SID")
        for i in ijin_db.objects.select_related('pegawai','ijin').filter(tgl_ijin__range=(dari,sampai)):
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


@login_required
def tambah_ijin(request):
    nama_user = request.user.username
    
    dtgl = request.POST.get('tgl')
    dpegawai = request.POST.get('pegawai')
    dijin = request.POST.get('ijin')
    dket = request.POST.get('ket')
    
    ij = jenis_ijin_db.objects.get(id=int(dijin))
        
    ltgl = dtgl.split(', ')
    print(ltgl)
    for t in ltgl:
        tgl = datetime.strptime(t,'%d-%m-%Y')        
              
        if ijin_db.objects.select_related('pegawai','ijin').filter(pegawai_id=int(dpegawai), tgl_ijin=tgl.date()).exists():
            status = 'duplikat'
        else:
            if absensi_db.objects.select_related('pegawai').filter(pegawai_id=int(dpegawai), tgl_absen=tgl.date()).exists():
                ab = absensi_db.objects.select_related('pegawai').get(pegawai_id=int(dpegawai), tgl_absen=tgl.date())
                ab.keterangan_ijin = f'{ij.jenis_ijin}-({dket})'
                ab.save()
            else:
                pass 
                
            tambah = ijin_db(
                ijin_id = int(dijin),
                tgl_ijin = tgl.date(),
                pegawai_id = int(dpegawai),
                keterangan = dket,        
                add_by = nama_user,
                edit_by = nama_user
            )
            tambah.save()

            status = 'ok'    
    
    return JsonResponse({"status": status})


@login_required
def batal_ijin(request):
    nama_user = request.user.username

    id_ijin = request.POST.get('id')
    
    ij = ijin_db.objects.select_related('pegawai','ijin').get(id=int(id_ijin))
    tgl = ij.tgl_ijin
    idp = ij.pegawai_id
    nama_pegawai = ij.pegawai.nama
    jenis_ijin = ij.ijin.jenis_ijin
    try:
        ab = absensi_db.objects.get(pegawai_id=int(idp), tgl_absen=tgl)
    except:
        return JsonResponse({"status": "error"},status=400)
    ab.keterangan_ijin = None
    ab.save()
    
    histori = histori_hapus_db(
        delete_by = nama_user,
        delete_item = f"{jenis_ijin}-(a.n {nama_pegawai}, tgl:{tgl})"
    )
    histori.save()
    
    ij.delete()
    
    status = 'ok'    
    
    return JsonResponse({"status": status})




# Jenis Ijin
# ++++++++++++++
@login_required
def jenis_ijin(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Jenis Ijin'     
        }
        
        return render(request,'hrd_app/ijin/jenis_ijin.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@login_required
def jenis_ijin_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        jenis_ijin = jenis_ijin_db.objects.all()
        
        data = []

        for j in jenis_ijin:
            obj = {
                "pk":j.pk,
                "jenis_ijin":j.jenis_ijin
            }
            data.append(obj)
        return JsonResponse({"data":data},safe=False,status=200)

@login_required
def tjenis_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")

    if jenis_ijin_db.objects.filter(jenis_ijin=jenis_ijin).exists():
        status="duplikat"
    else:
        jenis_ijin_db(
            jenis_ijin=jenis_ijin
        ).save()
        status = "ok"
    return JsonResponse({"status":status},safe=False,status=200)

@login_required
def ejenis_ijin(r):
    jenis_ijin = r.POST.get("jenis_ijin")
    id = r.POST.get("id") 
    if jenis_ijin_db.objects.filter(~Q(id=int(id)),jenis_ijin=jenis_ijin).exists():
        status = "duplikat"
    else:
        jenis_ijin_db.objects.filter(id=int(id)).update(jenis_ijin=jenis_ijin)
        status = "ok"
    return JsonResponse({"status":status},safe=False,status=200)

@login_required
def hjenis_ijin(r):
    id = r.POST.get("id")
    jenis_ijin = r.POST.get("jenis_ijin")
    nama_user = r.user.username
    try:
        jenis_ijin_db.objects.get(pk=int(id)).delete()
        thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus jenis ijin : {jenis_ijin}'
        )
        thapus.save()
        status = 'Ok'
    except:
        status = "gagal menghapus" 
    return JsonResponse({"status":status},safe=False,status=200)


@login_required
def tcuti_melahirkan(r):
    dr = r.POST.get("dari")
    sp = r.POST.get("sampai")
    pegawai = r.POST.get("pegawai")

    try:
        pgw = pegawai_db.objects.get(pk=int(pegawai))
    except:
        return JsonResponse({"status":400,"msg":"data pegawai tidak ada"},status=400)
    dari = datetime.strptime(dr,'%d-%m-%Y').date()
    sampai = datetime.strptime(sp,"%d-%m-%Y").date()
    data = []
    if ijin_db.objects.filter(tgl_ijin__range=(dari,sampai),pegawai_id=pgw.pk,ijin__jenis_ijin=r'CM$').exists():
        return JsonResponse({"status":400,"msg":"Data ijin sudah ada","data":[]},status=400)
    ijin = jenis_ijin_db.objects.filter(jenis_ijin__iregex=r"CM$")
    if not ijin.exists():
        return JsonResponse({"status":400,"msg":"Jenis ijin tidak ada","data":[]},status=400)
    for i in range((sampai - dari).days +1 ):
        obj = {
            "pegawai_id":pgw.pk,
            "ijin_id":ijin[0].pk,
            "tgl_ijin":dari + timedelta(days=i),
            "keterangan":f"Dispensasi - Cuti Melahirkan"
        }
        data.append(obj)
    ijin_db.objects.bulk_create([ijin_db(**i) for i in data])
    return JsonResponse({"status":"ok"},status=200)
