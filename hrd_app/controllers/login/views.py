from hrd_app.controllers.lib import *
from django.db import transaction
from django.contrib.auth import views as auth_views,models, authenticate,login,logout, hashers, base_user
from django.contrib.auth.models import UserManager


# def auth_login(r):
#     username = r.POST.get("username")
#     cabang = r.POST.get("cabang")
#     user = models.User.objects.using(cabang).filter(username=username)
#     print(user)
#     if user.exists():
#         akses = akses_db.objects.using(cabang).filter(user_id=user[0].pk)
#         if akses.exists():     
#             akses_cabang = akses_cabang_db.objects.filter(user_id=user[0].pk)
#             if akses_cabang.exists():
#                 auth = authenticate(username=r.POST.get("username"),password=r.POST.get("password"))
#                 print(r.POST.get("username"),r.POST.get("password"),auth)
#                 if auth is not None:
#                     r.session["ccabang"] = cabang
#                     r.session["cabang"] = [ac.cabang.cabang for ac in akses_cabang]
#                     print(r.session["ccabang"])
#                     login(r,auth)
#                     return redirect("beranda")
#                 else:
#                     messages.error(r, 'Username atau password salah.')        
#                     return redirect('login')
#             else:
#                 messages.error(r, 'Data akses Cabang Anda belum di tentukan.')        
#                 return redirect("login")

#         else:    
#             messages.error(r, 'Data akses Anda belum di tentukan.')        
#             return redirect('login')
#     else:
#         messages.error(r, 'Username atau password salah.')        
#         return redirect('login')
def auth_login(r):
    username = r.POST.get("username")
    cabang = r.POST.get("cabang")
    
    try:
        user = User.objects.get(username=username)
    except models.User.DoesNotExist:
        messages.error(r, 'Username salah.')        
        return redirect('login')
    
    if not cabang_db.objects.filter(cabang__iregex=rf'{cabang}').exists():
        messages.error(r,"Cabang tidak ada")
        return redirect("login")
    cabang = cabang_db.objects.get(cabang__iregex=rf"{cabang}")
    # cek akses yang terdapat dicabang yang dipilih
    akses = akses_db.objects.using(cabang.cabang).filter(user_id=user.pk)
    if akses.exists():     
        # cek akses cabang 
        akses_cabang = akses_cabang_db.objects.filter(user_id=user.pk,cabang_id=cabang.pk)
        if akses_cabang.exists():
            if hashers.check_password(r.POST.get("password"),user.password):
                r.session["cabang"] = [ac.cabang.cabang for ac in akses_cabang_db.objects.filter(user_id=user.pk)]
                r.session["ccabang"] = cabang.cabang
                login(r,user)
                return redirect("beranda")
            else:
                messages.error(r, 'Password salah.')        
                return redirect('login')
                
        else:
            messages.error(r, 'Anda tidak memiliki akses ke cabang tersebut.')        
            return redirect("login")
    else:    
        messages.error(r, 'Data akses Anda belum di tentukan.')        
        return redirect('login')    

@authorization(["root","it"])
def pilih_cabang(r):
    iduser = r.session["user"]["id"]
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        cabang = cabang_db.objects.filter(cabang__in=r.session["cabang"])
        data = {
            'dsid': dsid,
            'modul_aktif' : 'Divisi',
            "staff":r.session["user"]["admin"],
            'akses' : akses,
            # "cabang":r.session["cabang"],
            "ccabang":r.session["ccabang"],
            "nama":r.session["user"]["nama"],
            "cabang":cabang,
        }
        return render(r,'hrd_app/login/pilih_cabang.html',data)
    else:
        messages.error(r,"Anda tidak memiliki akses")
        return redirect("beranda")

@authorization(["root","it"])
def registrasi(r,idcabang):
    iduser = r.session["user"]["id"]
    if not akses_cabang_db.objects.filter(user_id=iduser,cabang_id=int(idcabang)).exists():
        messages.error(r,"Anda tidak memiliki akses")
        return redirect("pilih_cabang")
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if cabang_db.objects.filter(id=int(idcabang)).exists():
            cabang = cabang_db.objects.get(id=int(idcabang))
            users = user_db.objects.using(cabang.cabang).all()
            divisi = divisi_db.objects.using(cabang.cabang).all()
            pegawai = pegawai_db.objects.using(cabang.cabang).all()
            status = status_pegawai_db.objects.using(cabang.cabang).all()
            cabangall = cabang_db.objects.all()
            data = {       
                'dsid': dsid,
                'modul_aktif' : 'Divisi',
                "staff":r.session["user"]["admin"],
                'akses' : akses,
                "cabang":r.session["cabang"],
                "ccabang":r.session["ccabang"],
                "nama":r.session["user"]["nama"],
                "cp":cabang,
                "ca":cabangall,
                "caid":idcabang,
                "users":users, 
                "divisi":divisi,
                "pegawai":pegawai,
                "status":status
            }
            
            return render(r,'hrd_app/login/register.html', data)
        else:
            messages.error(r,"Cabang tidak ada")
            return redirect("pilih_cabang")
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@authorization(["root"])
def proses_registrasi(r):
    iduser = r.session["user"]["id"]
    cabang = r.POST.get("cabang")
    # if cabang is not None or cabang != "":
    #     if not akses_cabang_db.objects.filter(user_id=iduser,cabang_id=int(cabang)).exists():
    #         messages.error(r,"Anda tidak memiliki akses")
    #         return redirect("registrasi",idcabang=caid)  
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id        
        username = r.POST.get("username")
        password = r.POST.get("password")
        kpassword = r.POST.get("kpassword")
        # nama_depan = r.POST.get("nama_depan")
        if password != kpassword:
            messages.error(r,"Password tidak cocok")
            return redirect("registrasi",idcabang=cabang)
        with transaction.atomic(using=r.session["ccabang"]):
            try:
                # jika divisi ada kata "all"
                # result = [rsl for rsl in divisi if re.match("(?i)all",rsl)]
                # jika cabang ada kata "all"
                # resultcabang = [rslc for rslc in cabang if re.match("(?i)all",rslc)]
                user_db(username=username,password=password).save()
                user = User.objects.get(username=username)
                for c in cabang_db.objects.all():
                    User.objects.create_user(id=user.pk,username=r.session["user"]["nama"],password=password).save(using=c.cabang)
                # +++
                # tambah akses level
                # if akses_db.objects.using(r.session["ccabang"]).filter(Q(user_id=user.pk) | Q(pegawai_id=int(pegawai))).exists():
                #     messages.error(r,"Akses user sudah ditentukan")
                #     return redirect("registrasi")
                # aksessimpan = akses_db(
                #     user_id=user.pk,
                #     akses=level_akses,
                #     pegawai_id=int(pegawai),
                #     sid_id=int(status)
                # )
                # # +++
                # # +++
                # # tambah akses cabang
                # if len(resultcabang) > 0:
                #     cabangas = ["tasik","sumedang","cirebon","garut","cihideung"]
                # else:
                #     cabangas = cabang
                # for cbg in cabangas:
                #     if akses_cabang_db.objects.using(r.session["ccabang"]).filter(user_id=user.pk,cabang=cbg).exists():
                #         continue
                #     else:
                #         akses_cabang_db(
                #             user_id=user.pk,
                #             cabang=cbg
                #         ).save(using=r.session["ccabang"])
                # # ++=
                # # +++
                # # tambah akses divisi di masing masing cabang
                # if len(result) > 0:
                #     divisir = divisi_db.objects.using(r.session["ccabang"]).all()
                # else:
                #     divisir = divisi_db.objects.using(r.session["ccabang"]).filter(id__in=divisi)
                # for div in divisir:
                #     if akses_divisi_db.objects.using(r.session["ccabang"]).filter(user_id=user.pk,divisi_id=div.pk).exists():
                #         continue
                #     akses_divisi_db(
                #         user_id=user.pk,
                #         divisi_id=div.pk
                #     ).save(using=r.session["ccabang"])
                # # +++
                # aksessimpan.save(using=r.session["ccabang"])
                return redirect("registrasi",idcabang=cabang)
            except Exception as e:
                transaction.set_rollback(True,using=r.session["ccabang"])
                messages.error(r,e)
                return redirect("registrasi",idcabang=cabang)
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    

@authorization(["root","it"])
def reset_password(r):
    iduser = r.session["user"]["id"]
        
    caid = r.POST.get("cabang")
    if caid is not None or caid != "":
        if not akses_cabang_db.objects.filter(user_id=iduser,cabang_id=int(caid)).exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("registrasi",idcabang=caid)
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        username = r.POST.get("user")
        password = r.POST.get("password")
        kpassword = r.POST.get("kpassword")
        if password != kpassword:
            messages.error(r,"Password tidak cocok")
            return redirect("registrasi")
        try:
            if not cabang_db.objects.filter(pk=int(caid)).exists():
                messages.error(r,"Cabang tidak ada")
                return redirect("registrasi",idcabang=caid)
            user = User.objects.get(pk=int(username))
            user.set_password(password)
            user.save()
            return redirect("registrasi",idcabang=caid)
        except Exception as e:
            messages.error(r,e)
            return redirect("registrasi",idcabang=caid)
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')

@authorization(["root","it"])
def akses_divisi(r):
    iduser = r.session["user"]["id"]
        
    caid = r.POST.get("cabang")
    if caid is not None or caid != "":
        if not akses_cabang_db.objects.filter(user_id=iduser,cabang_id=int(caid)).exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("registrasi",idcabang=caid)
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id        
        userids = r.POST.getlist("userd[]")
        divisid = r.POST.getlist("divisid[]")

        if not userids or not divisid or userids == "" or divisid == "" or len(userids) <= 0 or len(divisid) <= 0:
            messages.error(r,"Silahkan isi form dengan lengkap")
            return redirect("registrasi",idcabang=caid)
        # nama_depan = r.POST.get("nama_depan")
        with transaction.atomic():
            try:
                result = [rsl for rsl in divisid if re.match("(?i)all",rsl)]
                for userid in userids:
                    user = user_db.objects.filter(pk=userid).last()
                    if not user:
                        messages.error(r,"User tidak ada")
                        return redirect("registrasi",idcabang=caid)
                    else:
                        if not cabang_db.objects.filter(id=int(caid)):
                            messages.error(r,"Cabang tidak ada")
                            return redirect("registrasi",idcabang=caid)
                        cabang = cabang_db.objects.get(id=int(caid))
                        
                        akses_divisi_db.objects.using(cabang.cabang).filter(user_id=user.pk).delete()
                        if len(result) > 0:
                            divisir = divisi_db.objects.using(cabang.cabang).all()
                        else:
                            divisir = divisi_db.objects.using(cabang.cabang).filter(id__in=divisid)
                        for div in divisir:
                            if akses_divisi_db.objects.using(cabang.cabang).filter(user_id=user.pk,divisi_id=div.pk).exists():
                                continue
                            akses_divisi_db(
                                user_id=user.pk,
                                divisi_id=div.pk
                            ).save(using=cabang.cabang)
                return redirect("registrasi",idcabang=caid)
            except Exception as e:
                messages.error(r,e)
                transaction.set_rollback(True)
                return redirect("registrasi",idcabang=caid)
    else:   
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    
@authorization(["root","it"])
def akses_level(r):
    iduser = r.session["user"]["id"]
    caid = r.POST.get("cabang")
    if caid is not None or caid != "":
        if not akses_cabang_db.objects.filter(user_id=iduser,cabang_id=int(caid)).exists():
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("registrasi",idcabang=caid)
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if not cabang_db.objects.filter(id=int(caid)).exists():
            messages.error(r,"Cabang tidak ada")
            return redirect("pilih_cabang")
        cabang = cabang_db.objects.get(id=int(caid))
        userid = r.POST.get("userl")
        level = r.POST.getlist("level_aksesl")
        # pegawai = r.POST.get("pegawai")
        status = r.POST.get("statuspegawai")
        if not userid or not level or not status or userid == '' or level == '' or status == '' :
            messages.error(r,"Silahkan isi form dengan lengkap")
            return redirect("registrasi",idcabang=caid)

        user = user_db.objects.filter(pk=userid)
        if not user.exists():
            messages.error(r,"User tidak ada")
            return redirect("registrasi",idcabang=caid)
        # nama_depan = r.POST.get("nama_depan")
        try:
            akses_db.objects.using(cabang.cabang).filter(user_id=userid).delete()
            # if not pegawai_db.objects.using(cabang.cabang).filter(id=int(pegawai)):
            #     messages.error(r,"Pegawai tidak ada")
            #     return redirect("registrasi",idcabang=caid)
            if not status_pegawai_db.objects.using(cabang.cabang).filter(id=int(status)):
                messages.error(r,'Status tidak ada')
                return redirect("registrasi",idcabang=caid)
            # pegawai_id = int(pegawai)
            sid_id = int(status)
            
            akses_db(
                user_id=userid,
                akses=level[0],
                pegawai=None,
                sid_id=sid_id
                ).save(using=cabang.cabang)
            return redirect("registrasi",idcabang=caid)
        except Exception as e:
            messages.error(r,e)
            return redirect("registrasi",idcabang=caid)
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    
@authorization(["root","it"])
def akses_cabang(r):
    iduser = r.session["user"]["id"]
    
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if r.session["user"]["admin"]:
            
            caid = r.POST.get("cabang")
            userids = r.POST.getlist("userc[]")
            cabang = r.POST.getlist("cabang[]")
            # nama_depan = r.POST.get("nama_depan")
            with transaction.atomic():
                try:
                    for userid in userids:
                        user = User.objects.filter(pk=userid)
                        if not user.exists():
                            messages.error(r,"User tidak ada")
                            return redirect("registrasi")
                        else:
                            result = [c for c in cabang if re.match("(?i)all",c)]
                            
                            akses_cabang_db.objects.filter(user_id=int(user[0].pk)).delete()
                            if len(result) > 0:
                                cabangs = [c.pk for c in cabang_db.objects.all()]
                            else:
                                cabangs = cabang
                            for cbg in cabangs:
                                akses_cabang_db(
                                    user_id=user[0].pk,
                                    cabang_id=int(cbg),
                                    add_by=r.session["user"]["nama"],
                                    edit_by=r.session["user"]["nama"]
                                ).save()
                    return redirect("registrasi",idcabang=caid)
                except Exception as e:
                    messages.error(r,e)
                    transaction.set_rollback(True)
                    return redirect("registrasi",idcabang=caid)
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("beranda")
    else:    
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')
    

@authorization(["root","it"])
def superuser(r):
    iduser = r.session["user"]["id"]
    if akses_db.objects.using(r.session["ccabang"]).filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.using(r.session["ccabang"]).get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        if r.session["user"]["admin"]:
            username = r.POST.get("username")
            cabang = r.POST.get("cabang")
            password = r.POST.get("password")
            kpassword = r.POST.get("kpassword")
            try:
                if password != kpassword:
                    messages.error(r,"Password anda tidak cocok")
                    return redirect("registrasi",idcabang=cabang)
                else:
                    User.objects.create_user(username=username,password=password,is_staff=True,is_superuser=True).save()
                    user = User.objects.get(username=username)
                    for c in cabang_db.objects.all():
                        User.objects.create_user(id=user.pk,username=username,password=password,is_staff=True,is_superuser=True).save(using=c.cabang)
                    return redirect("registrasi",idcabang=cabang)
            except Exception as e:
                messages.error(r,e)
                return redirect("registrasi",idcabang=cabang)
        else:
            messages.error(r,"Anda tidak memiliki akses")
            return redirect("registrasi",idcabang=cabang)
        

@authorization(["root","it"])
def ganti_password(r):
    id_user = r.session["user"]["id"]
    akses = akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    if akses is not None:
        return redirect(os.environ.get("CHANGE_PASS"))
    else:
        messages.error(r,"Akses anda belum ditentukan")
        return redirect("beranda")
    
@authorization(["root","it"])
def ganti_password_json(r):
    id_user = r.session["user"]["id"]
    akses =akses_db.objects.using(r.session["ccabang"]).filter(user_id=id_user).last()
    if akses is not None:
        pwLama = r.POST.get("pwLama")
        pwBaru = r.POST.get("pwBaru")
        konfirmasi = r.POST.get("konfirmasi")

        userLama = User.objects.using(r.session["ccabang"]).filter(pk=id_user).last()
        if not userLama:
            return JsonResponse({"status":"error","msg":"User tidak ada"},status=400)
        auth = hashers.check_password(pwLama,userLama.password)
        if auth is not None:
            if pwBaru == konfirmasi:
                # Root user
                user = User.objects.filter(pk=id_user).last()
                user.set_password(pwBaru)
                user.save()
                cabang = akses_cabang_db.objects.using(r.session["ccabang"]).filter(user_id=id_user)
                for c in cabang:
                    # Cabang user
                    userCabang = User.objects.using(c.cabang).filter(pk=id_user).last()
                    userCabang.set_password(pwBaru)
                    userCabang.save(using=c.cabang)

                return JsonResponse({"status":"success","msg":"Berhasil update password"},status=200)
            else:
                return JsonResponse({"status":"error","msg":"Password tidak sama"},status=400)
        else:
            return JsonResponse({"status":"error",'msg':"Password lama salah"},status=400)
    else:
        return JsonResponse({"status":"error","msg":"Akses anda belum ditentukan"},status=400)