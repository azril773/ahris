from django.urls import path
from hrd_app import views

urlsAjaxJamKerja = [
    path('jam_kerja_json', views.jam_kerja_json, name='jam_kerja_json'),
    path('edit_jkerja', views.edit_jam_kerja, name='edit_jkerja'),
    path('hapus_jkerja', views.hapus_jam_kerja, name='hapus_jkerja'),
    path('tjamkerja', views.tambah_jam_kerja, name='tjamkerja'),
    path('tkk_json', views.tambah_kk_json, name='tkk_json'),
    path('ekk_json', views.edit_kk_json, name='ekk_json'),
]


urlsRenderJamKerja = [
    path('jam_kerja', views.jam_kerja, name='jam_kerja'),
]