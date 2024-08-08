from django.urls import path
from hrd_app import views

urlsAjaxIjin = [


    path('ijin_json/<str:dr>/<str:sp>/<int:sid>', views.ijin_json, name='ijin_json'),    
    path('tijin', views.tambah_ijin, name='tijin'),
    path('bijin', views.batal_ijin, name='bijin'),
    path('tjenis_ijin', views.tjenis_ijin, name='tjenis_ijin'),
    path('ejenis_ijin', views.ejenis_ijin, name='ejenis_ijin'),
    path('hjenis_ijin', views.hjenis_ijin, name='hjenis_ijin'),
    path('jenis_ijin_json', views.jenis_ijin_json, name='jenis_ijin_json'),
]

urlsRenderIjin = [
    path('ijin/<int:sid>', views.ijin, name='ijin'),
    path('cijin', views.cari_ijin, name='cijin'),
    path('cijin_s/<str:dr>/<str:sp>/<int:sid>', views.cari_ijin_sid, name='cijin_s'),
    path('jenis_ijin', views.jenis_ijin, name='jenis_ijin'),
]