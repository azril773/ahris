from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("laporan_json", views.laporan_json, name="laporan_json"),
    path("laporan_json_periode/<int:sid>/<int:id>/<str:dr>/<str:sp>", views.laporan_json_periode, name="laporan_json_periode"),
    path("laporan_periode_excel/<int:sid>/<int:id>/<str:bulan>/<str:tahun>", views.laporan_json_periode_excel, name="laporan_json_periode_excel"),
]