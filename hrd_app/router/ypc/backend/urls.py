from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("tlengkap_json/<int:sid>",views.tlengkap_json,name="tlengkap_json"),
    path("tketerangan_json/<int:sid>",views.tketerangan_json,name="tketerangan_json"),
    path("terlambat_json/<int:sid>",views.terlambat_json,name="terlambat_json")
]