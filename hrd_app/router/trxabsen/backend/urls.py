from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("trxabsen_non",views.trxabsen_non,name="trxabsen_non"),
    path("trxabsen_json",views.trxabsen_json,name="trxabsen_json"),
    path("trxabsen_json_userid",views.filtertrx,name="trxabsen_json_userid"),
]