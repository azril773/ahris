from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('proses_registrasi', views.proses_registrasi, name='proses_registrasi'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('akses_divisi', views.akses_divisi, name='akses_divisi'),
    path('akses_level', views.akses_level, name='akses_level'),
    path('akses_cabang', views.akses_cabang, name='akses_cabang'),
    path('superuser', views.superuser, name='superuser'),
    path('tlibur_nasional', views.tambah_libur_nasional, name='tlibur_nasional'),
    path('elibur_nasional', views.edit_libur_nasional, name='elibur_nasional'),
    path('hlibur_nasional', views.hapus_libur_nasional, name='hlibur_nasional'),
]