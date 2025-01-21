from hrd_app.controllers.lib import *


# Status Pegawai
# ++++++++++++++
@authorization(["root","it"])
def status_pegawai(r):
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
            'modul_aktif' : 'Status Pegawai'     
        }
        
        return render(r,'hrd_app/status_pegawai/status_pegawai.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["root","it"])
def status_pegawai_json(r):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in status_pegawai_db.objects.using(r.session["ccabang"]).all().order_by('id'):
            
            sp = {
                'id':i.id,
                'status':i.status,
            }
            data.append(sp)
                                
        return JsonResponse({"data": data})


@authorization(["root","it"])
def tambah_status_pegawai(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dstatus = r.POST.get('status')
        
        if status_pegawai_db.objects.using(r.session["ccabang"]).filter(status = dstatus).exists():
            status = 'duplikat'
        else:    
            tstatus = status_pegawai_db(
                status = dstatus
            )
            tstatus.save(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@authorization(["root","it"])
def edit_status_pegawai(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = r.POST.get('eid')
        dstatus = r.POST.get('estatus')
        
        if status_pegawai_db.objects.using(r.session["ccabang"]).filter(status = dstatus).exists():
            status = 'duplikat'
        else:    
            nstatus = status_pegawai_db.objects.using(r.session["ccabang"]).get(id=int(eid))
            nstatus.status = dstatus
            nstatus.save(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@authorization(["root","it"])
def hapus_status_pegawai(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = r.session["user"]["nama"]
        
        hid = r.POST.get('hid')
        
        if pegawai_db.objects.using(r.session["ccabang"]).filter(status_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki status ini'
        else:        
            nstatus = status_pegawai_db.objects.using(r.session["ccabang"]).get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus status pegawai : {nstatus.status}'
            )
            thapus.save(using=r.session["ccabang"])
            
            nstatus.delete(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})
    

# ++++++++++++++
@authorization(["root","it"])
def status_pegawai_lh(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        status_pegawai = status_pegawai_db.objects.using(r.session["ccabang"]).all()
        data = {       
            'dsid': dsid,
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            "status":status_pegawai,
            'modul_aktif' : 'Status Pegawai Lintas Hari'     
        }
        
        return render(r,'hrd_app/status_pegawai/status_pegawai_lintas_hari.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["root","it"])
def status_pegawai_json_lh(r):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        for i in status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).all().order_by('id'):
            
            sp = {
                'pk':i.id,
                'status':i.status_pegawai.status,
            }
            data.append(sp)
        return JsonResponse({"data": data})

@authorization(["root","it"])
def tstatus_pegawai_lh(r):
    status = r.POST.get("status")
    
    if status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).filter(status_pegawai_id=status).exists():
        return JsonResponse({'status':'duplikat'},safe=False,status=400)
    else:
        status_pegawai_lintas_hari_db(status_pegawai_id=int(status)).save(using=r.session["ccabang"])
        return JsonResponse({'status':'berhasil'},safe=False,status=201)


@authorization(["root","it"])
def estatus_pegawai_lh(r):
    status = r.POST.get("status")
    id = r.POST.get('id')

    try:
        get = status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).filter(pk=int(id)).update(status_pegawai_id=int(status))
        return JsonResponse({'status':'ok'},safe=False,status=200)
    except Exception as err:
        
        return JsonResponse({"status":"gagal update"},safe=False,status=400)

@authorization(["root","it"])
def hstatus_pegawai_lh(r):
    id = r.POST.get('id')
    nama_user = r.session["user"]["nama"]

    try:
        get = status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus status pegawai lintas hari : {get.status_pegawai.status}'
        ).save(using=r.session["ccabang"])
        status_pegawai_lintas_hari_db.objects.using(r.session["ccabang"]).get(pk=int(id)).delete(using=r.session["ccabang"])
        return JsonResponse({'status':'ok'},safe=False,status=200)
    except:
        return JsonResponse({"status":"gagal hapus"},safe=False,status=400)

# ++++++++++++++
@authorization(["root","it"])
def status_pegawai_payroll(r):
    iduser = r.session["user"]["id"]
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        status_pegawai = status_pegawai_db.objects.using(r.session["ccabang"]).all()
        data = {       
            'dsid': dsid,
            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            "status":status_pegawai,
            'modul_aktif' : 'Status Pegawai Payroll'     
        }
        
        return render(r,'hrd_app/status_pegawai/status_pegawai_payroll.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["root","it"])
def status_pegawai_json_payroll(r):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
        for i in status_pegawai_payroll_db.objects.using(r.session["ccabang"]).all().order_by('id'):
            
            sp = {
                'pk':i.id,
                'status':i.status_pegawai.status,
            }
            data.append(sp)
        return JsonResponse({"data": data})

@authorization(["root","it"])
def tstatus_pegawai_payroll(r):
    status = r.POST.get("status")
    
    if status_pegawai_payroll_db.objects.using(r.session["ccabang"]).filter(status_pegawai_id=status).exists():
        return JsonResponse({'status':'duplikat'},safe=False,status=400)
    else:
        status_pegawai_payroll_db(status_pegawai_id=int(status)).save(using=r.session["ccabang"])
        return JsonResponse({'status':'berhasil'},safe=False,status=201)


@authorization(["root","it"])
def estatus_pegawai_payroll(r):
    status = r.POST.get("status")
    id = r.POST.get('id')

    try:
        get = status_pegawai_payroll_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        status_pegawai_payroll_db.objects.using(r.session["ccabang"]).filter(pk=int(id)).update(status_pegawai_id=int(status))
        return JsonResponse({'status':'ok'},safe=False,status=200)
    except Exception as err:
        
        return JsonResponse({"status":"gagal update"},safe=False,status=400)

@authorization(["root","it"])
def hstatus_pegawai_payroll(r):
    id = r.POST.get('id')
    nama_user = r.session["user"]["nama"]

    try:
        get = status_pegawai_payroll_db.objects.using(r.session["ccabang"]).get(pk=int(id))
        histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus status pegawai payroll : {get.status_pegawai.status}'
        ).save(using=r.session["ccabang"])
        status_pegawai_payroll_db.objects.using(r.session["ccabang"]).get(pk=int(id)).delete(using=r.session["ccabang"])
        return JsonResponse({'status':'ok'},safe=False,status=200)
    except:
        return JsonResponse({"status":"gagal hapus"},safe=False,status=400)



@authorization(["root","it"])
def sstatus_payroll(r):
    id_user = r.session["user"]["id"]
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user):
        akses = akses_db.objects.using(r.session["ccabang"]).get(user_id=id_user)
        akses = akses.akses
        status = status_pegawai_db.objects.using(r.session["ccabang"]).all()
        for s in status:
            status_pegawai_payroll_app_db(
                id=s.pk,
                status=s.status,
            ).save(using=f'p{r.session["ccabang"]}')
    else:
        pass 