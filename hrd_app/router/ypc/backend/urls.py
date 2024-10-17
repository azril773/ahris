from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("tlengkap_json/",views.tlengkap_json,name="tlengkap_json")
]