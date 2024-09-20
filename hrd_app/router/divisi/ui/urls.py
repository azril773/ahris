from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('divisi', views.divisi, name='divisi'),
]