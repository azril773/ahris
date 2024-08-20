from django.urls import path
from hrd_app.controllers import views



urlpatterns = [
    path('geser_off/<int:sid>', views.geser_off, name='geser_off'),
    path('geser_off/<str:dr>/<str:sp>/<int:sid>', views.cari_geser_off_sid, name='cgeser_off_s'),
    path('geser_off', views.cari_geser_off, name='cgeser_off'),
    
]