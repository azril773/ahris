from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('libur_nasional', views.libur_nasional, name='libur_nasional'),
]