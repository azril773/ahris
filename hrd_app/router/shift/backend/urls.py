from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("shift_json",views.shift_json,name="shift_json"),
    path("tshift_json",views.tshift_json,name="tshift_json"),
    path("eshift_json",views.eshift_json,name="eshift_json"),
    path("hshift_json",views.hshift_json,name="hshift_json"),
]