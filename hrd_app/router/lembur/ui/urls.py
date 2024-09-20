from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('lembur/<int:sid>', views.lembur, name='lembur'),
    path('cari_lembur', views.cari_lembur, name='clembur'),
    path('belum_proses/<int:sid>', views.lembur_belum_proses, name='lembur_bproses'),
    path('proses_ulembur/<int:idl>', views.proses_ulang_lembur, name='proses_ulembur'),
    path('tlembur', views.tambah_lembur, name='tlembur'),


]