from django.urls import path
from hrd_app import views

urlsAjaxStatusPegawai = [
    path('status_pegawai_json', views.status_pegawai_json, name='status_pegawai_json'),
    path('tstatus_pegawai', views.tambah_status_pegawai, name='tstatus_pegawai'),
    path('estatus_pegawai', views.edit_status_pegawai, name='estatus_pegawai'),
    path('hstatus_pegawai', views.hapus_status_pegawai, name='hstatus_pegawai'),


    path('estatus_pegawai_lembur', views.estatus_pegawai_lembur, name='espgl'),
    path('tstatus_pegawai_lembur', views.tstatus_pegawai_lembur, name='tspgl'),
    path('hstatus_pegawai_lembur', views.hstatus_pegawai_lembur, name='hspgl'),
    path('status_pegawai_lembur_json', views.status_pegawai_lembur_json, name='spgljson'),
]

urlsRenderStatusPegawai = [
    path('status_pegawai_lembur', views.status_pegawai_lembur, name='status_pegawai_lembur'),
    path('status_pegawai', views.status_pegawai, name='status_pegawai'),
]
