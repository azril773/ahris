from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    # deprecated
    path('cabsen_s/<str:dr>/<str:sp>/<int:sid>', views.cari_absensi_sid, name='cabsen_s'),
    # deprecated

    
    path('absensi/<int:sid>', views.absensi, name='absensi'),
    path('dabsen/<str:userid>/<str:tgl>/<int:sid>', views.detail_absensi, name='dabsen'),
    path('edit_jamkerja/<str:userid>/<str:tgl>/<int:sid>', views.edit_jamkerja, name='edit_jamkerja'),
] 