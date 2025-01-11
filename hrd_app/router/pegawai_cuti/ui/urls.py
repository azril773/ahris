from django.urls import path
from hrd_app.controllers import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('pegawai_cuti', views.pegawai_cuti, name='pegawai_cuti'),
    

]