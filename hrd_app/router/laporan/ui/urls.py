from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('laporan/<int:sid>', views.laporan, name='laporan'),
    path('print_laporan/<int:sid>/<int:id>/<str:bulan>/<str:tahun>', views.print_laporan, name='print_laporan'),
    path('print_laporan_pegawai/', views.print_laporan_pegawai, name='print_laporan_pegawai'),
] 