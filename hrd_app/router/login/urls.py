from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('', views.auth_login, name='auth_login'),
]