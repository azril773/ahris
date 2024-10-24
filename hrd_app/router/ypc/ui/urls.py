from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("tlengkap/<int:sid>",views.tlengkap,name="tlengkap"),
    path("tketerangan/<int:sid>",views.tketerangan,name="tketerangan"),
    path("terlambat/<int:sid>",views.terlambat,name="terlambat"),
]