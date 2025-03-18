from django.urls import path
from hrd_app.controllers import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("getPegawai/<int:idp>",views.getPegawai,name="getPegawai"),
    path('tambah_pegawai/', views.tambah_pegawai, name='tambah_pegawai'),
    path('tambah_pegawai_non_validasi/', views.tambah_pegawai_non_validasi, name='tambah_pegawai_non_validasi'),
    path('edit_pegawai/<int:idp>', views.epegawai, name='edit_pegawai'),
    path('pegawai_json/<int:sid>', views.pegawai_json, name='pegawai_json'),
    path('non_aktif_json/<int:sid>', views.non_aktif_json, name='non_aktif_json'),
    path('history_pegawai_json/<int:sid>', views.history_pegawai_json, name='history_pegawai_json'),
    path('detail_history_json/<int:sid>/<int:idp>', views.detail_history_json, name='detail_history_json'),
    path('detail_data_json', views.detail_data_json, name='detail_data_json'),
    path('keluarga_data_json', views.keluarga_data_json, name='keluarga_data_json'),
    path('pihak_data_json', views.pihak_data_json, name='pihak_data_json'),
    path('pengalaman_data_json', views.pengalaman_data_json, name='pengalaman_data_json'),
    path('pendidikan_data_json', views.pendidikan_data_json, name='pendidikan_data_json'),
    path('history_pribadi_json', views.history_pribadi_json, name='history_pribadi_json'),
    path('anon', views.aktif_nonaktif, name='anon'),
    path('nonaktif', views.nonaktif, name='nonaktif'),
    path('aktif', views.aktif, name='aktif'),
    path('tkeluarga/<int:idp>', views.tambah_keluarga, name='tkeluarga'),
    path('tkl/<int:idp>', views.tambah_kl, name='tkl'),
    path('ambil_mesin/', views.ambil_mesin, name='ambil_mesin'),
    path('upload_foto/', views.upload_foto, name='upload_foto'),
    path('hapusfinger/', views.hapusfinger, name='hapusfinger'),
]
