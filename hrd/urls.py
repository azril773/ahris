from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views # type: ignore
from hrd_app.admin import cirebon, tasik, sumedang, cihideung,garut
import debug_toolbar
import os
from django.contrib import messages 
import re
from hrd_app.models import user_db, akses_cabang_db, cabang_db
import json
from authlib.integrations.django_client import OAuth
oauth = OAuth()
oauth.register("oidc",client_id=os.environ.get("CLIENT_ID"), client_secret=os.environ.get("CLIENT_SECRET"), authorize_url=os.environ.get("AUTHORIZE_URL"),server_metadata_url=os.environ.get("CONFIG_URL") ,access_token_url=os.environ.get("TOKEN_URL"))
def login(r):
    return oauth.oidc.authorize_redirect(r,os.environ.get("REDIRECT_URI"))


def callback(r):
    token = oauth.oidc.authorize_access_token(r)
    r.session["token"] = token
    access = oauth.oidc.get(os.environ.get("USERINFO_URL"),token=token)
    result = access.json()

    groups = "".join(result["groups"])
    getCabang = re.findall('ahris_(cirebon|tasik|sumedang|garut|cihideung)',groups,re.IGNORECASE)
    if len(getCabang) <= 0:
        messages.error(r,"Anda tidak memiliki akses ke cabang manapun")
        return redirect("beranda")
    
    is_admin = [True if re.search("authentik Admins",groups,re.IGNORECASE) is not None else False]

    user = user_db.objects.filter(sub=result["sub"]).last()
    if not user:
        user_db(
            sub=result["sub"],
            email=result["email"],
            nama=result["name"],
            is_admin=is_admin[0]
        ).save()
        user = user_db.objects.filter(sub=result["sub"]).last()
    else:
        user.email = result["email"]
        user.nama = result["name"]
        user.is_admin = is_admin[0]
        user.save()

    cbgs = cabang_db.objects.filter(cabang__in=getCabang)
    for c in cbgs:
        if not user_db.objects.using(c.cabang).filter(sub=result["sub"]).exists():
            user_db(
                pk=user.pk,
                sub=result["sub"],
                email=result["email"],
                nama=result["name"],
                is_admin=is_admin[0]
            ).save(using=c.cabang)
        else:
            user_db.objects.using(c.cabang).filter(sub=result["sub"]).update(email=result["email"],nama=result["name"],is_admin=is_admin[0])

        if not akses_cabang_db.objects.filter(cabang_id=c.pk,user_id=user.pk):
            akses_cabang_db(
                cabang_id=c.pk,
                add_by=result["name"],
                user_id=user.pk
            ).save()

    
    r.session["cabang"] = getCabang
    r.session["ccabang"] = getCabang[0]
    r.session["user"] = {
        "id":user.pk,
        "sub":user.sub,
        "email":user.email,
        "nama":user.nama,
        "admin":user.is_admin
    }
    return redirect("/hrd/absensi/0")

def beranda(r): 
    auth = False
    nama = None
    cabang = ''
    ccabang = []
    try:
        if r.session["user"] and r.session["ccabang"] and r.session["cabang"]:
            user = r.session["user"]
            auth = True
            nama = user["nama"]
            cabang = r.session["cabang"]
            ccabang = r.session["ccabang"]
        else:
            pass
    except:
        pass

    data = {
        "cabang":cabang,
        "ccabang":ccabang,
        "sid":0,
        'dsid':0,
        "nama":nama,
        "auth":auth,
        "dashboard":"http://15.59.254.57:9000"
    }
    return render(r,"hrd_app/beranda.html",data)
    
    
urlpatterns = [
    path('adminnya/', admin.site.urls),
    path('callback/', callback),
    path('cirebonadmin/', cirebon.urls),
    path('tasikadmin/', tasik.urls),
    path('sumedangadmin/', sumedang.urls),
    path('cihideungadmin/', cihideung.urls),
    path('garutadmin/', garut.urls),
    path('', beranda),
    path("__debug__/",include(debug_toolbar.urls)),
    path("login/",login,name='login'),
    path("beranda/",beranda,name='beranda'),
    # path("login/",include("hrd_app.router.login.urls")),
    path('hrd/', include('hrd_app.router.urls')),
] 
