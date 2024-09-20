from hrd_app.controllers.lib import *


# Divisi
# ++++++++++++++
@login_required
def divisi(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Divisi'     
        }
        
        return render(request,'hrd_app/divisi/divisi.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def divisi_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in divisi_db.objects.all().order_by('divisi'):
            
            div = {
                'id':i.id,
                'divisi':i.divisi,
            }
            data.append(div)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_divisi(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        ddiv = request.POST.get('divisi')
        
        if divisi_db.objects.filter(divisi = ddiv).exists():
            status = 'duplikat'
        else:    
            tdiv = divisi_db(
                divisi = ddiv,
            )
            tdiv.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_divisi(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        ddiv = request.POST.get('edivisi')
        
        if divisi_db.objects.filter(divisi = ddiv).exists():
            status = 'duplikat'
        else:    
            ndiv = divisi_db.objects.get(id=int(eid))
            ndiv.divisi = ddiv
            ndiv.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_divisi(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
        
        if pegawai_db.objects.filter(divisi_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki divisi ini'
        else:        
            ndiv = divisi_db.objects.get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus divisi : {ndiv.divisi}'
            )
            thapus.save()
            
            ndiv.delete()
            
            status = 'ok'
        
        return JsonResponse({"status": status})

