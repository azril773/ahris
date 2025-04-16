from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('absensi_json/<str:dr>/<str:sp>/<int:sid>', views.absensi_json, name='absensi_json'),    
    path('pbs', views.pabsen, name='pbs'),    
    path('get_trans_json', views.get_trans_json, name='get_trans_json'),    
    path('get_raw_json', views.get_raw_json, name='get_raw_json'),    
    path('hapus_jam', views.hapus_jam, name='hapus_jam'),
    path('tambah_jam', views.tambah_jam, name='tambah_jam'),
    path('ubah_absen', views.ubah_absen, name='ubah_absen'),
    path('cabsen', views.cari_absensi, name='cabsen'),  


    path('pu/<str:tgl>/<int:userid>/<int:sid>/<str:dr>/<str:sp>', views.pu, name='pu'),
    path('edit_ijin', views.edit_ijin, name='edit_ijin'),

    path("absensi_id",views.absensi_id,name="absensi_id"),
]