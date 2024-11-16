from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('status_pegawai_lembur', views.status_pegawai_lembur, name='status_pegawai_lembur'),
    path('status_pegawai_libur_nasional', views.status_pegawai_libur_nasional, name='status_pegawai_libur_nasional'),
    path('status_pegawai_opg', views.status_pegawai_opg, name='status_pegawai_opg'),
    path('status_pegawai_lh', views.status_pegawai_lh, name='status_pegawai_lh'),
    path('status_pegawai_payroll', views.status_pegawai_payroll, name='status_pegawai_payroll'),
    path('status_pegawai', views.status_pegawai, name='status_pegawai'),
    path('sstatus_payroll', views.sstatus_payroll, name='sstatus_payroll'),
]
