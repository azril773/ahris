from hrd_app.controllers.lib import *

# Libur Nasional
# ++++++++++++++
@login_required
def libur_nasional(r):
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
            'modul_aktif' : 'Libur Nasional'     
        }
        
        return render(r,'hrd_app/libur_nasional/libur_nasional.html', data)
        
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def libur_nasional_json(r):
        
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in libur_nasional_db.objects.using(r.session["ccabang"]).all().order_by('tgl_libur'):
            
            tgl = i.tgl_libur.strftime('%d-%m-%Y')
            insentif = "{:,.0f}".format(i.insentif_karyawan)
            
            ln = {
                'id': i.id,
                'libur': i.libur,
                'tgl': tgl,
                'insentif': insentif.replace(',', '.')
            }
            data.append(ln)
                                
        return JsonResponse({"data": data})


@login_required
def tambah_libur_nasional(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dtgl = r.POST.get('tgl')
        libur = r.POST.get('libur')
        dinsentif = r.POST.get('insentif')
        
        tgl = datetime.strptime(dtgl, '%d-%m-%Y').date()
        insentif = dinsentif.replace('.', '')
        
        if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur = tgl).exists():
            status = 'duplikat'
        else:    
            ln = libur_nasional_db(
                tgl_libur = tgl,
                libur = libur,
                insentif_karyawan = insentif,
            )
            ln.save(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_libur_nasional(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = r.POST.get('eid')
        dtgl = r.POST.get('etgl')
        libur = r.POST.get('elibur')
        dinsentif = r.POST.get('einsentif')
        
        tgl = datetime.strptime(dtgl, '%d-%m-%Y').date()
        insentif = dinsentif.replace('.', '')
        
        if libur_nasional_db.objects.using(r.session["ccabang"]).filter(tgl_libur = tgl, libur = libur, insentif_karyawan = insentif).exists():
            status = 'duplikat'
        else:    
            ln = libur_nasional_db.objects.using(r.session["ccabang"]).get(id=int(eid))
            ln.tgl_libur = tgl
            ln.libur = libur
            ln.insentif_karyawan = insentif
            ln.save(using=r.session["ccabang"])
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_libur_nasional(r):
    
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = r.user.username
        
        hid = r.POST.get('hid')
              
        ln = libur_nasional_db.objects.using(r.session["ccabang"]).get(id=int(hid))            
        
        thapus = histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus libur nasional : {ln.libur}'
        )
        thapus.save(using=r.session["ccabang"])
        
        ln.delete(using=r.session["ccabang"])
        
        status = 'ok'
        
        return JsonResponse({"status": status})
