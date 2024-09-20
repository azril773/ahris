from hrd_app.controllers.lib import *


# Counter
# ++++++++++++++
@login_required
def counter(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Counter'     
        }
        
        return render(request,'hrd_app/pengaturan/counter.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def counter_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in counter_db.objects.all().order_by('counter'):
            
            ct = {
                'id':i.id,
                'counter':i.counter,
            }
            data.append(ct)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_counter(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dcounter = request.POST.get('counter')
        
        if counter_db.objects.filter(counter = dcounter).exists():
            status = 'duplikat'
        else:    
            tc = counter_db(
                counter = dcounter,
            )
            tc.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_counter(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        dcounter = request.POST.get('ecounter')
        
        if counter_db.objects.filter(counter = dcounter).exists():
            status = 'duplikat'
        else:    
            nct = counter_db.objects.get(id=int(eid))
            nct.counter = dcounter
            nct.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_counter(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
        
        if pegawai_db.objects.filter(counter_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki counter ini'
        else:        
            nct = counter_db.objects.get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus counter : {nct.counter}'
            )
            thapus.save()
            
            nct.delete()
            
            status = 'ok'
        
        return JsonResponse({"status": status})

