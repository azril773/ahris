from hrd_app.controllers.lib import *

# Libur Nasional
# ++++++++++++++
@login_required
def libur_nasional(request):
    iduser = request.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Libur Nasional'     
        }
        
        return render(request,'hrd_app/libur_nasional/libur_nasional.html', data)
        
    else:    
        messages.info(request, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')


@login_required
def libur_nasional_json(request):
        
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        data = []
                
        for i in libur_nasional_db.objects.all().order_by('tgl_libur'):
            
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
def tambah_libur_nasional(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        dtgl = request.POST.get('tgl')
        libur = request.POST.get('libur')
        dinsentif = request.POST.get('insentif')
        
        tgl = datetime.strptime(dtgl, '%d-%m-%Y').date()
        insentif = dinsentif.replace('.', '')
        
        if libur_nasional_db.objects.filter(tgl_libur = tgl).exists():
            status = 'duplikat'
        else:    
            ln = libur_nasional_db(
                tgl_libur = tgl,
                libur = libur,
                insentif_karyawan = insentif,
            )
            ln.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def edit_libur_nasional(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        eid = request.POST.get('eid')
        dtgl = request.POST.get('etgl')
        libur = request.POST.get('elibur')
        dinsentif = request.POST.get('einsentif')
        
        tgl = datetime.strptime(dtgl, '%d-%m-%Y').date()
        insentif = dinsentif.replace('.', '')
        
        if libur_nasional_db.objects.filter(tgl_libur = tgl, libur = libur, insentif_karyawan = insentif).exists():
            status = 'duplikat'
        else:    
            ln = libur_nasional_db.objects.get(id=int(eid))
            ln.tgl_libur = tgl
            ln.libur = libur
            ln.insentif_karyawan = insentif
            ln.save()
            
            status = 'ok'
        
        return JsonResponse({"status": status})


@login_required
def hapus_libur_nasional(request):
    
    if request.headers["X-Requested-With"] == "XMLHttpRequest":
        
        nama_user = request.user.username
        
        hid = request.POST.get('hid')
              
        ln = libur_nasional_db.objects.get(id=int(hid))            
        
        thapus = histori_hapus_db(
            delete_by = nama_user,
            delete_item = f'hapus libur nasional : {ln.libur}'
        )
        thapus.save()
        
        ln.delete()
        
        status = 'ok'
        
        return JsonResponse({"status": status})

