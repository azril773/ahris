from hrd_app.controllers.lib import *

@login_required
def pegawai_cuti(r):
    id_user = r.user.id
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    if akses is not None:
        if akses.akses == "root" or akses.akses == "it":
            
            aksesdivisi = [d.divisi.pk for d in akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)]
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(divisi_id__in=aksesdivisi)
            data = {       
                'dsid': akses.sid_id,

                'akses' : akses,
                "cabang":r.session["cabang"],
                "ccabang":r.session["ccabang"],
                "pegawai":pegawai,
                'modul_aktif' : 'Pegawai Cuti'     
            }
            return render(r,"hrd_app/pegawai_cuti/pegawai_cuti.html",data)

@login_required
def pegawai_cuti_json(r):
    pass

@login_required
def tpegawai_cuti_json(r):
    print("oksokDOSK")
    idps = r.POST.getlist("pegawai[]")
    
    failed = idps
    pegawai = pegawai_db.objects.using(r.session["ccabang"]).filter(pk__in=idps)
    for p in pegawai:
        if str(p.pk) in idps:
            failed.remove(str(p.pk))
        with transaction.atomic(using=r.session["ccabang"]):
            try:
                if pegawai_cuti_lama.objects.using(r.session["ccabang"]).filter(pegawai_id=p.pk).exists():
                    return JsonResponse({"status":'error',"msg":"Data sudah ada"},status=400)
                pegawai_cuti_lama.objects.using(r.session['ccabang']).create(pegawai_id=p.pk)
            except Exception as e:
                transaction.set_rollback(True,using=r.session["ccabang"])
                return JsonResponse({"status":"error","msg":"Terjadi Kesalahan"},status=400)
        return JsonResponse({"status":"success","msg":"tambah data berhasil","failed":failed},status=201)

@login_required
def epegawai_cuti_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id = r.POST.get("eid")
        eidp = r.POST.get("eidp")
        print(id,eidp)
        if not id or not eidp:
            return JsonResponse({"status":'error',"msg":"Isi form dengan lengkap"},status=400)
        if not pegawai_cuti_lama.objects.using(r.session["ccabang"]).filter(pk=int(id)).exists():
            return JsonResponse({"status":"error","msg":"Data tidak ada"},status=400)

        if not pegawai_db.objects.using(r.session["ccabang"]).filter(pk=eidp):
            return JsonResponse({"status":"error","msg":"Pegawai tidak ada"},status=400)
        
        if pegawai_cuti_lama.objects.using(r.session["ccabang"]).filter(~Q(pk=int(id)),pegawai_id=int(eidp)).exists():
            return JsonResponse({"status":'error',"msg":"Data sudah ada"},status=400)
        pegawai_cuti_lama.objects.using(r.session["ccabang"]).filter(pk=id).update(pegawai_id=eidp)
        return JsonResponse({'status':"success","msg":"Berhasil edit data"},status=200)



@login_required
def dpegawai_cuti_json(r):
    if r.headers["X-Requested-With"]:
        id = r.POST.get("id")
        if not id:
            return JsonResponse({"status":'error',"msg":"Isi form dengan lengkap"},status=400)
        if not pegawai_cuti_lama.objects.using(r.session['ccabang']).filter(pk=int(id)).exists():
            return JsonResponse({"status":'error','msg':"Data tidak ada"},status=400)

        pegawai_cuti_lama.objects.using(r.session["ccabang"]).filter(pk=int(id)).delete()
        return JsonResponse({'status':"success","msg":"Berhasil hapus data"},status=200)


@login_required
def pegawai_cuti_json(r):
    if r.headers["X-Requested-With"] == "XMLHttpRequest":
        id_user = r.user.id
        akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
        if akses is not None:
            if akses.akses == "root" or akses.akses == "it":                        
                data = []

                for p in pegawai_cuti_lama.objects.using(r.session["ccabang"]).all():
                    obj = {
                        "id":p.pk,
                        "nama":p.pegawai.nama,
                        "idp":p.pegawai_id
                    }
                    data.append(obj)

                return JsonResponse({"status":"success","msg":"Berhasil ambil data","data":data},status=200)
