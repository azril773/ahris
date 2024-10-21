from django.urls import path
from hrd_app.controllers import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('pegawai/<int:sid>', views.pegawai, name='pegawai'),
    path('epegawai/<int:idp>', views.edit_pegawai, name='epegawai'),
    path('tpegawai/', views.tpegawai, name='tpegawai'),
    path('non_aktif/<int:sid>', views.pegawai_non_aktif, name='non_aktif'),
    path('general_data/<int:idp>', views.general_data, name='general_data'),
    path('general_data_nonaktif/<int:idp>', views.general_data_nonaktif, name='general_data_nonaktif'),
    path('dapri/<int:idp>', views.data_pribadi, name='dapri'),
    path('dapri_nonaktif/<int:idp>', views.data_pribadi_nonaktif, name='dapri_nonaktif'),
    path('pkerja/<int:idp>', views.pendidikan_kerja, name='pkerja'),
    path('pkerja_nonaktif/<int:idp>', views.pendidikan_kerja_nonaktif, name='pkerja_nonaktif'),
    path('registrasi_pegawai', views.registrasi_pegawai, name='registrasi_pegawai'),
    path('rp_mesin', views.rp_mesin, name='rp_mesin'),
    path('rp_form', views.rp_form, name='rp_form'),
    path('rp_cmesin', views.rp_cmesin, name='rp_cmesin'),
    path('rpm', views.rpm, name='rpm'),


]