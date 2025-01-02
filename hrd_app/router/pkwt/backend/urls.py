from django.urls import path
from hrd_app.controllers import views
from django.contrib.auth import views as auth_views


urlpatterns = [
path("pkwt_json",views.pkwt_json,name="pkwt_json")

]