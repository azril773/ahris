from django.urls import path
from hrd_app import views

urlsAjaxOpg = [
    path('opg_json/<str:dr>/<str:sp>/<int:sid>',views.opg_json, name='opg_json'),
    path('topg', views.tambah_opg, name='topg'),
    path('popg', views.pakai_opg, name='popg'),
    path('bopg', views.batal_opg, name='bopg'),
    path('hopg', views.hapus_opg, name='hopg'),
]

urlsRenderOpg = [
    path('opg/<int:sid>', views.opg, name='opg'),
    path('copg', views.cari_opg, name='copg'),
    path('copg_s/<str:dr>/<str:sp>/<int:sid>', views.cari_opg_sid, name='copg_s'),
]