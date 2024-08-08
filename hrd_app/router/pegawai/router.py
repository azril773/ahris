from django.urls import path
from hrd_app import views
from django.contrib.auth import views as auth_views

urlsAjaxPegawai = [
    path("getPegawai/<int:idp>",views.getPegawai,name="getPegawai"),
    path('tambah_pegawai/', views.tambah_pegawai, name='tambah_pegawai'),
    path('edit_pegawai/<int:idp>', views.epegawai, name='edit_pegawai'),
]


urlsRenderPegawai = [
    path('pegawai/<int:sid>', views.pegawai, name='pegawai'),
    path('epegawai/<int:idp>', views.edit_pegawai, name='epegawai'),
    path('tpegawai/', views.tpegawai, name='tpegawai'),
    path('non_aktif/<int:sid>', views.pegawai_non_aktif, name='non_aktif'),
]