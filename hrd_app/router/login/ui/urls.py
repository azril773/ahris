from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('registrasi', views.registrasi, name='registrasi'),
    path('tlibur_nasional', views.tambah_libur_nasional, name='tlibur_nasional'),
    path('elibur_nasional', views.edit_libur_nasional, name='elibur_nasional'),
    path('hlibur_nasional', views.hapus_libur_nasional, name='hlibur_nasional'),
]