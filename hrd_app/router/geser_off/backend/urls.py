from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('gf_json/<str:dr>/<str:sp>/<int:sid>', views.geseroff_json, name='gf_json'),
    path('tgf', views.tambah_geseroff, name='tgf'),
    path('bgf', views.batal_geseroff, name='bgf'),
]