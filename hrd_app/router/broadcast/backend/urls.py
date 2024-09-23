
from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("spk/",views.single_perjanjian_kontrak,name="spk"),
    path("spa/",views.single_absensi,name="spa"),
]