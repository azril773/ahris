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

]