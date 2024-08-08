from django.urls import path
from hrd_app import views

urlsAjaxDivisi = [
    path('divisi_json', views.divisi_json, name='divisi_json'),
    path('tdivisi', views.tambah_divisi, name='tdivisi'),
    path('edivisi', views.edit_divisi, name='edivisi'),
    path('hdivisi', views.hapus_divisi, name='hdivisi'),
]

urlsRenderDivisi = [
    path('divisi', views.divisi, name='divisi'),
]