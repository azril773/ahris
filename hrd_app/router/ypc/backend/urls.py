from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("tlengkap_json/",views.tlengkap_json,name="tlengkap_json"),
    path("tketerangan_json/",views.tketerangan_json,name="tketerangan_json"),
    path("terlambat_json/",views.terlambat_json,name="terlambat_json")
]