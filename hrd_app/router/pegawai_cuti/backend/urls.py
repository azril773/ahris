from django.urls import path
from hrd_app.controllers import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('pegawai_cuti_json', views.pegawai_cuti_json, name='pegawai_cuti_json'),
    path('tpegawai_cuti_json', views.tpegawai_cuti_json, name='tpegawai_cuti_json'),
    path('epegawai_cuti_json', views.epegawai_cuti_json, name='epegawai_cuti_json'),
    path('dpegawai_cuti_json', views.dpegawai_cuti_json, name='dpegawai_cuti_json'),

]