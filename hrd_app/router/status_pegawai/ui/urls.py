from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('status_pegawai_lembur', views.status_pegawai_lembur, name='status_pegawai_lembur'),
    path('status_pegawai', views.status_pegawai, name='status_pegawai'),
]
