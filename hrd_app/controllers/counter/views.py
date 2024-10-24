from hrd_app.controllers.lib import *


# Counter
# ++++++++++++++
@login_required
def counter(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Counter'     
        }
        
        return render(r,'hrd_app/pengaturan/counter.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def counter_json(r):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in counter_db.objects.using(r.session["ccabang"]).all().order_by('counter'):
            
            ct = {
                'id':i.id,
                'counter':i.counter,
            }
            data.append(ct)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_counter(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dcounter = r.POST.get('counter')
        
        if counter_db.objects.using(r.session["ccabang"]).filter(counter = dcounter).exists():
            status = 'duplikat'
        else:    
            tc = counter_db(
                counter = dcounter,
            )
            tc.save(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_counter(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = r.POST.get('eid')
        dcounter = r.POST.get('ecounter')
        
        if counter_db.objects.using(r.session["ccabang"]).filter(counter = dcounter).exists():
            status = 'duplikat'
        else:    
            nct = counter_db.objects.using(r.session["ccabang"]).get(id=int(eid))
            nct.counter = dcounter
            nct.save(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_counter(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = r.user.username
        
        hid = r.POST.get('hid')
        
        if pegawai_db.objects.filter(counter_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki counter ini'
        else:        
            nct = counter_db.objects.using(r.session["ccabang"]).get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus counter : {nct.counter}'
            )
            thapus.save(using=r.session["ccabang"])
            
            nct.delete()
            
            status = 'ok'
        
        return JsonResponse({"status": status})

