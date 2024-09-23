
from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("broadcast/<int:sid>",views.broadcast,name="broadcast"),
    path("read_absensi",views.ra,name="ra")
]