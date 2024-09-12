from django.urls import path
from hrd_app.controllers import views



urlpatterns = [
    path('jam_kerja', views.jam_kerja, name='jam_kerja'),
]