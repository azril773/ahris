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
        if akses == 'root' or akses == 'it':
            users = User.objects.all()
            divisi = divisi_db.objects.all()
            pegawai = pegawai_db.objects.all()
            status = status_pegawai_db.objects.all()
            data = {       
                'dsid': dsid,
                'modul_aktif' : 'Divisi',

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
        if akses == 'root' or akses == 'it':
        
            username = r.POST.get("username")
            password = r.POST.get("password")
            divisi = r.POST.getlist("divisi[]")
            level_akses = r.POST.get("level_akses")
            pegawai = r.POST.get("pegawai")
            status = r.POST.get("status")
            kpassword = r.POST.get("kpassword")
            # nama_depan = r.POST.get("nama_depan")
            if password != kpassword:
                messages.error(r,"Password tidak cocok")
                return redirect("registrasi")
            try:
                result = [rsl for rsl in divisi if re.match("(?i)all",rsl)]
                print(result)
                User.objects.create_user(username=username,password=password).save()
                user = User.objects.get(username=username)
                if akses_db.objects.filter(Q(user_id=user.pk) | Q(pegawai_id=int(pegawai))).exists():
                    messages.error(r,"Akses user sudah ditentukan")
                    return redirect("registrasi")
                akses_db(
                    user_id=user.pk,
                    akses=level_akses,
                    pegawai_id=int(pegawai),
                    sid_id=int(status)
                ).save()
                if len(result) > 0:
                    divall = divisi_db.objects.all()
                    for div in divall:
                        if akses_divisi_db.objects.filter(user_id=user.pk,divisi_id=div.pk).exists():
                            continue
                        akses_divisi_db(
                            user_id=user.pk,
                            divisi_id=div.pk
                        ).save()
                else:
                    divfil = divisi_db.objects.filter(id__in=divisi)
                    for div in divfil:
                        if akses_divisi_db.objects.filter(user_id=user.pk,divisi_id=div.pk).exists():
                            continue
                        akses_divisi_db(
                            user_id=user.pk,
                            divisi_id=div.pk
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
                    user = User.objects.get(pk=userid)
                    print(userid)
                    akses_divisi_db.objects.filter(user_id=user.pk).delete()
                    if len(result) > 0:
                        divall = divisi_db.objects.all()
                        for div in divall:
                            if akses_divisi_db.objects.filter(user_id=user.pk,divisi_id=div.pk).exists():
                                continue
                            akses_divisi_db(
                                user_id=user.pk,
                                divisi_id=div.pk
                            ).save()
                    else:
                        divfil = divisi_db.objects.filter(id__in=divisid)
                        for div in divfil:
                            if akses_divisi_db.objects.filter(user_id=user.pk,divisi_id=div.pk).exists():
                                continue
                            akses_divisi_db(
                                user_id=user.pk,
                                divisi_id=div.pk
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
                    akses_db(
                        user_id=userid,
                        akses=level,
                        pegawai_id=aksesdb[0].pegawai_id,
                        sid_id=aksesdb[0].sid_id
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