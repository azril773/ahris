from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('absensi_json/<str:dr>/<str:sp>/<int:sid>', views.absensi_json, name='absensi_json'),    
    path('pbs', views.pabsen, name='pbs'),    
]