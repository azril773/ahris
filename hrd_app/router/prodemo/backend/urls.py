from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('tambah_prodemo/',views.tambah_prodemo,name="tambah_prodemo"),
    path("promodemo_json/<int:idp>/<int:aktif>",views.promodemo_json,name="promodemo_json"),
]