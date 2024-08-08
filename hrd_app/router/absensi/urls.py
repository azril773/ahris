from django.urls import path
from hrd_app import views
urlpatterns = [
    path('absensi_json/<str:dr>/<str:sp>/<int:sid>', views.absensi_json, name='absensi_json'),    
    path('pbs', views.pabsen, name='pbs'),    
]

# urlsRenderAbsensi = [
#     path('absensi/<int:sid>', views.absensi, name='absensi'),
#     path('cabsen', views.cari_absensi, name='cabsen'),  
#     path('cabsen_s/<str:dr>/<str:sp>/<int:sid>', views.cari_absensi_sid, name='cabsen_s'),
# ] 