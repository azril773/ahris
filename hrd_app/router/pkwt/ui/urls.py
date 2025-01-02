from django.urls import path
from hrd_app.controllers import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('pkwt', views.pkwt, name='pkwt'),
    

]