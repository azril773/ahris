from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("trxabsen",views.trxabsen,name="trxabsen"),
]