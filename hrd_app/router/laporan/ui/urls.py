from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('laporan/<int:sid>', views.laporan, name='laporan'),
] 