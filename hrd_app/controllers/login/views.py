from hrd_app.controllers.lib import *
from django.db import transaction
from django.contrib.auth import views as auth_views,models, authenticate,login,logout



def auth_login(r):
    username = r.POST.get("username")
    user = models.User.objects.filter(username=username)
    if user.exists():
        akses = akses_db.objects.filter(user_id=user[0].pk)
        if akses.exists():     
            akses_cabang = akses_cabang_db.objects.filter(user_id=user[0].pk)
            if akses_cabang.exists():
                auth = authenticate(username=r.POST.get("username"),password=r.POST.get("password"))
                if auth is not None:
                    r.session["ccabang"] = akses_cabang[0].cabang
                    r.session["cabang"] = [akses.cabang for akses in akses_cabang]
                    login(r,user[0])
                    return redirect("beranda")
                else:
                    messages.error(r, 'Username atau password salah.')        
                    return redirect('login')
            else:
                messages.error(r, 'Data akses Cabang Anda belum di tentukan.')        
                return redirect("login")

        else:    
            messages.error(r, 'Data akses Anda belum di tentukan.')        
            return redirect('login')
    else:
        messages.error(r, 'Username atau password salah.')        
        return redirect('login')
        



@login_required
def registrasi(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if akses == 'root' or akses == "it":
            users = User.objects.all()
            divisi = divisi_db.objects.using(r.session["ccabang"]).all()
            pegawai = pegawai_db.objects.using(r.session["ccabang"]).all()
            status = status_pegawai_db.objects.using(r.session["ccabang"]).all()
            data = {       
                'dsid': dsid,
                'modul_aktif' : 'Divisi',
                "staff":r.user.is_staff,
                'akses' : akses,
                "cabang":r.session["cabang"],
                "ccabang":r.session["ccabang"],
                "users":users, 
                "divisi":divisi,
                "pegawai":pegawai,
                "status":status
            }
            
            return render(r,'hrd_app/login/register.html', data)
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@login_required
def proses_registrasi(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if akses == 'root':
        
            username = r.POST.get("username")
            password = r.POST.get("password")
            divisi = r.POST.getlist("divisi[]")
            cabang = r.POST.getlist("cabang[]")
            level_akses = r.POST.get("level_akses")
            pegawai = r.POST.get("pegawai")
            status = r.POST.get("status")
            kpassword = r.POST.get("kpassword")
            # nama_depan = r.POST.get("nama_depan")
            if password != kpassword:
                messages.error(r,"Password tidak cocok")
                return redirect("registrasi")
            with transaction.atomic(using=r.session['ccabang']):
                try:
                    # jika divisi ada kata "all"
                    result = [rsl for rsl in divisi if re.match("(?i)all",rsl)]

                    # jika cabang ada kata "all"
                    resultcabang = [rslc for rslc in cabang if re.match("(?i)all",rslc)]

                    User.objects.create_user(username=username,password=password).save()

                    user = User.objects.get(username=username)

                    # +++
                    # tambah akses level
                    if akses_db.objects.filter(Q(user_id=user.pk) | Q(pegawai_id=int(pegawai))).exists():
                        messages.error(r,"Akses user sudah ditentukan")
                        return redirect("registrasi")
                    aksessimpan = akses_db(
                        user_id=user.pk,
                        akses=level_akses,
                        pegawai_id=int(pegawai),
                        sid_id=int(status)
                    )
                    # +++


                    # +++
                    # tambah akses cabang
                    if len(resultcabang) > 0:
                        cabangas = ["tasik","sumedang","cirebon","garut","cihideung"]
                    else:
                        cabangas = cabang

                    for cbg in cabangas:
                        User.objects.using(cbg).filter(id=user.pk).delete()
                        User.objects.create_user(id=user.pk,username=username,password=password).save(using=cbg)
                        if akses_cabang_db.objects.filter(user_id=user.pk,cabang=cbg):
                            continue
                        else:
                            akses_cabang_db(
                                user_id=user.pk,
                                cabang=cbg
                            ).save()
                    # ++=

                    # +++
                    # tambah akses divisi di masing masing cabang
                    if len(result) > 0:
                        divisir = divisi_db.objects.using(r.session["ccabang"]).all()
                    else:
                        divisir = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=divisi)

                    for div in divisir:
                        if akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=user.pk,divisi_id=div.pk).exists():
                            continue
                        akses_divisi_db(
                            user_id=user.pk,
                            divisi_id=div.pk
                        ).save(using=r.session["ccabang"])
                    # +++
                    aksessimpan.save()
                    return redirect("registrasi")
                except Exception as e:
                    transaction.set_rollback(True,using=r.session["ccabang"])
                    messages.error(r,e)
                    return redirect("registrasi")
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")

    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    

@login_required
def reset_password(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if akses == 'root' or akses == 'it':
            username = r.POST.get("user")
            password = r.POST.get("password")
            kpassword = r.POST.get("kpassword")
            # nama_depan = r.POST.get("nama_depan")
            if password != kpassword:
                messages.error(r,"Password tidak cocok")
                return redirect("registrasi")
            try:
                user = User.objects.get(pk=username)
                user.set_password(password)
                user.save()
                return redirect("registrasi")
            except Exception as e:
                messages.error(r,e)
                return redirect("registrasi")
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@login_required
def akses_divisi(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if akses == 'root' or akses == 'it':
        
            userid = r.POST.get("userd")
            divisid = r.POST.getlist("divisid[]")
            # nama_depan = r.POST.get("nama_depan")
            with transaction.atomic():
                try:
                    result = [rsl for rsl in divisid if re.match("(?i)all",rsl)]
                    user = User.objects.filter(pk=userid)
                    if not user.exists():
                        messages.error(r,"User tidak ada")
                    else:
                        user = user[0]
                        print(user)
                        akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=user.pk).delete()
                        if len(result) > 0:
                            divisir = divisi_db.objects.using(r.session["ccabang"]).all()
                        else:
                            divisir = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=divisid)

                        for div in divisir:
                            if akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=user.pk,divisi_id=div.pk).exists():
                                continue
                            akses_divisi_db(
                                user_id=user.pk,
                                divisi_id=div.pk
                            ).save(using=r.session["ccabang"])
                        return redirect("registrasi")
                except Exception as e:
                    messages.error(r,e)
                    transaction.set_rollback(True)
                    return redirect("registrasi")
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    
@login_required
def akses_level(r):
    iduser = r.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if akses == 'root' or akses == 'it':
        
            userid = r.POST.get("userl")
            level = r.POST.getlist("level_aksesl")
            # nama_depan = r.POST.get("nama_depan")
            try:
                user = User.objects.get(pk=userid)
                aksesdb = akses_db.objects.filter(user_id=userid)
                if not aksesdb.exists():
                    messages.error(r,"User belum ada akses")
                    return redirect("registrasi")
                else:
                    pegawai_id = aksesdb[0].pegawai_id
                    sid_id = aksesdb[0].sid_id
                    aksesdb.delete()
                    print(level)
                    akses_db(
                        user_id=userid,
                        akses=level[0],
                        pegawai_id=pegawai_id,
                        sid_id=sid_id
                    ).save()
                return redirect("registrasi")
            except Exception as e:
                messages.error(r,e)
                return redirect("registrasi")
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    
@login_required
def akses_cabang(r):
    iduser = r.user.id
    
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if r.user.is_staff:
            print("OK")
            userid = r.POST.get("userc")
            cabang = r.POST.getlist("cabang[]")
            # nama_depan = r.POST.get("nama_depan")
            with transaction.atomic():
                try:
                    user = User.objects.filter(pk=userid)
                    if not user.exists():
                        messages.error(r,"User tidak ada")
                        return redirect("registrasi")
                    else:
                        result = [c for c in cabang if re.match("(?i)all",c)]
                        print(result)
                        akses_cabang_db.objects.filter(user_id=int(user[0].pk)).delete()
                        if len(result) > 0:
                            cabangs = ["tasik","sumedang","cirebon","garut","cihideung"]
                        else:
                            cabangs = cabang
                        for cbg in cabangs:
                            akses_cabang_db(
                                user_id=user[0].pk,
                                cabang=cbg,
                                add_by="prog",
                                edit_by="prog"
                            ).save()
                    return redirect("registrasi")
                except Exception as e:
                    messages.error(r,e)
                    transaction.set_rollback(True)
                    return redirect("registrasi")
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')