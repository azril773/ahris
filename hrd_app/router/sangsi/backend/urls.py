from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('get_sangsi_pegawai/<int:idp>', views.get_sangsi_pegawai, name='get_sangsi_pegawai'),
    path('sangsi_json/<int:idp>/<int:aktif>', views.sangsi_json, name='sangsi_json'),
    path('tambah_sangsi/<int:idp>', views.tambah_sangsi, name='tambah_sangsi'),
]