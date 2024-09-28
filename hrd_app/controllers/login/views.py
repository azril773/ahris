from hrd_app.controllers.lib import *

@login_required
def registrasi(r):
    iduser = r.user.id
        
    if akses_db.objects.filter(user_id=iduser).exists():
        
        dakses = akses_db.objects.get(user_id=iduser)
        akses = dakses.akses
        dsid = dakses.sid_id
        users = User.objects.all()
        data = {       
            'dsid': dsid,
            'modul_aktif' : 'Divisi',
            "users":users
        }
        
        return render(r,'hrd_app/login/register.html', data)
        
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
        
        username = r.POST.get("username")
        password = r.POST.get("password")
        kpassword = r.POST.get("kpassword")
        # nama_depan = r.POST.get("nama_depan")
        if password != kpassword:
            messages.error(r,"Password tidak cocok")
            return redirect("registrasi")
        try:
            User.objects.create_user(username=username,password=password).save()
            return redirect("registrasi")
        except Exception as e:
            messages.error(r,e)
            return redirect("registrasi")
        
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
        messages.info(r, 'Data akses Anda belum di tentukan.')        
        return redirect('beranda')