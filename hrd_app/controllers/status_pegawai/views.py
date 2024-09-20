from hrd_app.controllers.lib import *


# Status Pegawai
# ++++++++++++++
@login_required
def status_pegawai(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Status Pegawai'     
        }
        
        return render(request,'hrd_app/status_pegawai/status_pegawai.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def status_pegawai_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in status_pegawai_db.objects.all().order_by('id'):
            
            sp = {
                'id':i.id,
                'status':i.status,
            }
            data.append(sp)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_status_pegawai(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dstatus = request.POST.get('status')
        
        if status_pegawai_db.objects.filter(status = dstatus).exists():
            status = 'duplikat'
        else:    
            tstatus = status_pegawai_db(
                status = dstatus
            )
            tstatus.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_status_pegawai(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        dstatus = request.POST.get('estatus')
        
        if status_pegawai_db.objects.filter(status = dstatus).exists():
            status = 'duplikat'
        else:    
            nstatus = status_pegawai_db.objects.get(id=int(eid))
            nstatus.status = dstatus
            nstatus.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_status_pegawai(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
        
        if pegawai_db.objects.filter(status_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki status ini'
        else:        
            nstatus = status_pegawai_db.objects.get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus status pegawai : {nstatus.status}'
            )
            thapus.save()
            
            nstatus.delete()
            
            status = 'ok'
        
        return JsonResponse({"status": status})
