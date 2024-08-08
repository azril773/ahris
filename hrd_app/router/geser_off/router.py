from django.urls import path
from hrd_app import views
urlsAjaxGeserOff = [
    path('gf_json/<str:dr>/<str:sp>/<int:sid>', views.geseroff_json, name='gf_json'),
    path('tgf', views.tambah_geseroff, name='tgf'),
    path('bgf', views.batal_geseroff, name='bgf'),
]


urlsRenderGeserOff = [
    path('geser_off/<int:sid>', views.geser_off, name='geser_off'),
    path('geser_off/<str:dr>/<str:sp>/<int:sid>', views.cari_geser_off_sid, name='cgeser_off_s'),
    path('geser_off', views.cari_geser_off, name='cgeser_off'),
    
]