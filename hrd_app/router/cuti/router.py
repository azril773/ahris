from django.urls import path
from hrd_app import views

urlsAjaxCuti = [
    path('cuti_json/<str:dr>/<str:sp>/<int:sid>', views.cuti_json, name='cuti_json'),
    path('dcuti_json/<int:idp>', views.dcuti_json, name='dcuti_json'),
    
    path('tcuti', views.tambah_cuti, name='tcuti'),
    path('ecuti', views.edit_sisa_cuti, name='ecuti'),
    path('bcuti', views.batal_cuti, name='bcuti'),    
]

urlsRenderCuti = [
    path('cuti/<int:sid>', views.cuti, name='cuti'),
    path('cuti/<int:sid>/<int:idp>', views.detail_cuti, name='dcuti'),   
    path('ccuti', views.cari_cuti, name='ccuti'),
    
]