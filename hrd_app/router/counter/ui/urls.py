from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('counter', views.counter, name='counter'),
]