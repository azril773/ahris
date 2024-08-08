from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('opg_json/<str:dr>/<str:sp>/<int:sid>',views.opg_json, name='opg_json'),
    path('topg', views.tambah_opg, name='topg'),
    path('popg', views.pakai_opg, name='popg'),
    path('bopg', views.batal_opg, name='bopg'),
    path('hopg', views.hapus_opg, name='hopg'),
]