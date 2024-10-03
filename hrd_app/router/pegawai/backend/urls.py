from django.urls import path
from hrd_app.controllers import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("getPegawai/<int:idp>",views.getPegawai,name="getPegawai"),
    path('tambah_pegawai/', views.tambah_pegawai, name='tambah_pegawai'),
    path('edit_pegawai/<int:idp>', views.epegawai, name='edit_pegawai'),
    path('pegawai_json/<int:sid>', views.pegawai_json, name='pegawai_json'),
    path('non_aktif_json/<int:sid>', views.non_aktif_json, name='non_aktif_json'),
    path('anon', views.aktif_nonaktif, name='anon'),
    path('nonaktif', views.nonaktif, name='nonaktif'),
    path('aktif', views.aktif, name='aktif'),
    path('tkeluarga/<int:idp>', views.tambah_keluarga, name='tkeluarga'),
    path('tkl/<int:idp>', views.tambah_kl, name='tkl'),
]
