from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from hrd_app.admin import cirebon, tasik, sumedang, cihideung,garut
import debug_toolbar
from authlib.integrations.django_client import OAuth
oauth = OAuth()
def login(r):
    oauth.register("oidc",client_id="6GUBX52ZOgFneRjvMbcKiFUCsb7rmIRQ7hPYkYmG", client_secret="GKARnh0J9eBd8bmzDXxmkAufdfc3xWmbI2pILWszkHY2K8uhQdoGla5cofdLwk5fHFlHMaBnQ5XFy6AKI9tWlCTYWAj0g0rlNmmtIjckAXNCgjLLHVyZCJ5zkHp5mLAa", authorize_url="http://localhost:8002/application/o/authorize/", access_token_url="http://localhost:8002/application/o/token/")
    return oauth.oidc.authorize_redirect(r,"http://localhost:8000/callback")
def callback(r):
    token = oauth.oidc.authorize_access_token(r)
    access = oauth.oidc.get("http://localhost:8002/application/o/userinfo/",token=token)
    result = access.json()
    r.session["user"] = result
urlpatterns = [
    path('adminnya/', admin.site.urls),
    path('callback/', callback),
    path('cirebonadmin/', cirebon.urls),
    path('tasikadmin/', tasik.urls),
    path('sumedangadmin/', sumedang.urls),
    path('cihideungadmin/', cihideung.urls),
    path('garutadmin/', garut.urls),
    path('', auth_views.LoginView.as_view(template_name='hrd_app/login.html'), name='login'),
    path("__debug__/",include(debug_toolbar.urls)),
    path("login/",include("hrd_app.router.login.urls")),
    path('hrd/', include('hrd_app.router.urls')),
] 
