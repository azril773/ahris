from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('mesin_json/', views.mesin_json, name='mesin_json'),
    # path('dusermesin/<int:id>', views.dusermesin, name='dusermesin'),
    path('tambah_data_mesin/<int:id>', views.add_data, name='tdm'),
    path('tambah_data_pegawai', views.tambah_data_pegawai, name='tambah_data_pegawai'),
    path('cpalldata/', views.cpalldata, name='cpalldata'),
    path('cppegawai/', views.cppegawai, name='cppegawai'),
    path('cpdivisi/', views.cpdivisi, name='cpdivisi'),
    path('tambahdatamesin/', views.adduser_machine, name='tambahdatamesin'),
    path('editdatamesin/', views.edituser_machine, name='editdatamesin'),
    path('hapusdatamesin/', views.deleteuser_machine, name='hapusdatamesin'),
    path('hapusdatamesinu/', views.deleteuser_machineu, name='hapusdatamesinu'),
    path('hapusabsen/<int:id>', views.hapusabsen, name='hapusabsen'),
    path('sesuaikanjam/<int:id>', views.sesuaikanjam, name='sesuaikanjam'),
    path('clearbuffer/<int:id>', views.clearbuffer, name='clearbuffer'),
    path('tmesin', views.tmesin, name='tmesin'),
    path('hmesin', views.hmesin, name='hmesin'),
    path('emesin', views.emesin, name='emesin'),
    path('getmesin', views.getmesin, name='getmesin'),
    path('listdata_json', views.listdata_json, name='listdata_json'),

]