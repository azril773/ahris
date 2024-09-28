from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("laporan_json", views.laporan_json, name="laporan_json"),
    path("laporan_json_periode/<int:sid>/<int:id>/<str:dr>/<str:sp>", views.laporan_json_periode, name="laporan_json_periode"),
    
]