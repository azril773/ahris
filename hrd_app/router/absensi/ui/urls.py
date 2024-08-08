from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('absensi/<int:sid>', views.absensi, name='absensi'),
    path('cabsen', views.cari_absensi, name='cabsen'),  
    path('cabsen_s/<str:dr>/<str:sp>/<int:sid>', views.cari_absensi_sid, name='cabsen_s'),
] 