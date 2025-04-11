from hrd_app.controllers.lib import *


# Counter
# ++++++++++++++
@authorization(["*"])
def counter(r):
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
            'modul_aktif' : 'Counter'     
        }
        
        return render(r,'hrd_app/pengaturan/counter.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@authorization(["*"])
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


@authorization(["*"])
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


@authorization(["*"])
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


@authorization(["*"])
def hapus_counter(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = r.session["user"]["nama"]
        
        hid = r.POST.get('hid')
        
        if pegawai_db.objects.using(r.session["ccabang"]).filter(counter_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki counter ini'
        else:        
            nct = counter_db.objects.using(r.session["ccabang"]).get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus counter : {nct.counter}'
            )
            thapus.save(using=r.session["ccabang"])
            
            nct.delete(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})



@authorization(["*"])
def scounter_payroll(r):
    id_user = r.session["user"]["id"]
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user):
        akses = akses_db.objects.using(r.session["ccabang"]).get(user_id=id_user)
        akses = akses.akses
        counter = counter_db.objects.using(r.session["ccabang"]).all()
        for c in counter:
            counter_payroll_db(
                id=c.pk,
                counter=c.counter,
            ).save(using=f'p{r.session["ccabang"]}')
    else:
        pass