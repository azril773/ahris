from hrd_app.controllers.lib import *


# Divisi
# ++++++++++++++
@login_required
def divisi(r):
    iduser = r.user.id
        
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,

            'akses' : akses,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            'modul_aktif' : 'Divisi'     
        }
        
        return render(r,'hrd_app/divisi/divisi.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def divisi_json(r):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in divisi_db.objects.using(r.session["ccabang"]).all().order_by('divisi'):
            
            div = {
                'id':i.id,
                'divisi':i.divisi,
            }
            data.append(div)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_divisi(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        ddiv = r.POST.get('divisi')
        
        if divisi_db.objects.using(r.session["ccabang"]).filter(divisi = ddiv).exists():
            status = 'duplikat'
        else:    
            tdiv = divisi_db(
                divisi = ddiv,
            )
            tdiv.save(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_divisi(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = r.POST.get('eid')
        ddiv = r.POST.get('edivisi')
        
        if divisi_db.objects.using(r.session["ccabang"]).filter(divisi = ddiv).exists():
            status = 'duplikat'
        else:    
            ndiv = divisi_db.objects.using(r.session["ccabang"]).get(id=int(eid))
            ndiv.divisi = ddiv
            ndiv.save(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_divisi(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = r.user.username
        
        hid = r.POST.get('hid')
        
        if pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id=int(hid), aktif=1).exists():
            status = 'pegawai memiliki divisi ini'
        else:        
            ndiv = divisi_db.objects.using(r.session["ccabang"]).get(id=int(hid))            
            
            thapus = histori_hapus_db(
                delete_by = nama_user,
                delete_item = f'hapus divisi : {ndiv.divisi}'
            )
            thapus.save(using=r.session["ccabang"])
            
            ndiv.delete(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def sdivisi_payroll(r):
    id_user = r.user.id
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user):
        akses = akses_db.objects.using(r.session["ccabang"]).get(user_id=id_user)
        akses = akses.akses
        if akses == "root" or akses == "hrd":
            divisi = divisi_db.objects.using(r.session["ccabang"]).all()
            for d in divisi:
                divisi_payroll_db(
                    id=d.pk,
                    divisi=d.divisi,
                ).save(using=f'p{r.session["ccabang"]}')
        else:
            pass
    else:
        pass