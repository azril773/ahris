from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('ijin/<int:sid>', views.ijin, name='ijin'),
    path('cijin', views.cari_ijin, name='cijin'),
    path('cijin_s/<str:dr>/<str:sp>/<int:sid>', views.cari_ijin_sid, name='cijin_s'),
    path('jenis_ijin', views.jenis_ijin, name='jenis_ijin'),
]