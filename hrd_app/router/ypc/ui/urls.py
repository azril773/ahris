from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("tlengkap/",views.tlengkap,name="tlengkap"),
    path("terlambat/",views.terlambat,name="terlambat"),
    path("tketerangan/",views.tketerangan,name="tketerangan")
]