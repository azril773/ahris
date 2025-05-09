from hrd_app.controllers.lib import *


@authorization(["*"])
def shift(r):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
    if akses.exists():
        shift = shift_db.objects.using(r.session["ccabang"]).all()
        akses = akses[0]
        data = {
            'dsid':akses.sid_id,
            "akses":akses.akses,
            "shift":shift,
            "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            "modul_aktif":"Shift"
        }
        return render(r,"hrd_app/shift/shift.html",data)
    

@authorization(["*"])
def shift_json(r):
    shift = shift_db.objects.using(r.session["ccabang"])
    data = []
    for s in shift:
        obj = {
            "id":s.pk,
            "shift":s.shift,
        }
        data.append(obj)
    return JsonResponse({'status':"success","msg":"","data":data})



@authorization(["*"])
def tshift_json(r):
    shift = r.POST.get("shift")
    sh = shift_db.objects.using(r.session["ccabang"]).filter(shift=shift)
    if sh.exists():
        return JsonResponse({"status":"error","msg":"Shift sudah ada"},status=400)
    shift_db(
        shift=shift
    ).save(using=r.session["ccabang"])    
    return JsonResponse({'status':"success","msg":"Berhasil tambah shift"})


@authorization(["*"])
def eshift_json(r):
    shift = r.POST.get("shift")
    id = r.POST.get("id")
    sh = shift_db.objects.using(r.session["ccabang"]).filter(~Q(id=int(id)),shift=shift)
    if sh.exists():
        return JsonResponse({"status":"error","msg":"Shift sudah ada"},status=400)
    s = shift_db.objects.using(r.session["ccabang"]).filter(pk=int(id))
    if not s.exists():
        return JsonResponse({"status":"error","msg":"Shift tidak ada"},status=400)
    s.update(shift=shift)
    return JsonResponse({'status':"success","msg":"Berhasil edit shift"})


@authorization(["*"])
def hshift_json(r):
    id = r.POST.get("id")
    s = shift_db.objects.using(r.session["ccabang"]).filter(pk=int(id)).delete()
    return JsonResponse({'status':"success","msg":"Berhasil hapus shift"})