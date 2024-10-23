from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('status_pegawai_json', views.status_pegawai_json, name='status_pegawai_json'),
    path('tstatus_pegawai', views.tambah_status_pegawai, name='tstatus_pegawai'),
    path('estatus_pegawai', views.edit_status_pegawai, name='estatus_pegawai'),
    path('hstatus_pegawai', views.hapus_status_pegawai, name='hstatus_pegawai'),


    path('estatus_pegawai_lembur', views.estatus_pegawai_lembur, name='espgl'),
    path('tstatus_pegawai_lembur', views.tstatus_pegawai_lembur, name='tspgl'),
    path('hstatus_pegawai_lembur', views.hstatus_pegawai_lembur, name='hspgl'),
    path('status_pegawai_lembur_json', views.status_pegawai_lembur_json, name='spgljson'),
    

    path('estatus_pegawai_libur_nasional', views.estatus_pegawai_libur_nasional, name='espgln'),
    path('tstatus_pegawai_libur_nasional', views.tstatus_pegawai_libur_nasional, name='tspgln'),
    path('hstatus_pegawai_libur_nasional', views.hstatus_pegawai_libur_nasional, name='hspgln'),
    path('status_pegawai_libur_nasional_json', views.status_pegawai_libur_nasional_json, name='spglnjson'),


    path('estatus_pegawai_opg', views.estatus_pegawai_opg, name='espgopg'),
    path('tstatus_pegawai_opg', views.tstatus_pegawai_opg, name='tspgopg'),
    path('hstatus_pegawai_opg', views.hstatus_pegawai_opg, name='hspgopg'),
    path('status_pegawai_opg_json', views.status_pegawai_opg_json, name='spgopgjson'),
]