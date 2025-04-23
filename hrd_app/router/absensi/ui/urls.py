from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    # deprecated
    path('cabsen_s/<str:dr>/<str:sp>/<int:sid>', views.cari_absensi_sid, name='cabsen_s'),
    # deprecated

    
    path('absensi/<int:sid>', views.absensi, name='absensi'),
    path('absensi/<int:sid>/<str:dr>/<str:sp>', views.absensi_tgl, name='absensi_tgl'),
    path('dabsen/<str:userid>/<str:tgl>/<int:sid>/<str:dr>/<str:sp>', views.detail_absensi, name='dabsen'),
    path('dabsen_non/<str:userid>/<str:tgl>/<int:sid>', views.detail_absensi_non, name='dabsen_non'),
    path('edit_jamkerja/<str:userid>/<str:tgl>/<int:sid>/<str:dr>/<str:sp>', views.edit_jamkerja, name='edit_jamkerja'),
    path('edit_jamkerja_non/<str:userid>/<str:tgl>/<int:sid>', views.edit_jamkerja_non, name='edit_jamkerja_non'),
] 