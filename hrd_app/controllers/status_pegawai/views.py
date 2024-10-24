from hrd_app.controllers.lib import *


# Status Pegawai
# ++++++++++++++
@login_required
def status_pegawai(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Status Pegawai'     
        }
        
        return render(r,'hrd_app/status_pegawai/status_pegawai.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
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


@login_required
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


@login_required
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


@login_required
def hapus_status_pegawai(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = r.user.username
        
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
