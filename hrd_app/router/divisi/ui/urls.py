from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('divisi', views.divisi, name='divisi'),
    path('sdivisi_payroll', views.sdivisi_payroll, name='sdivisi_payroll'),
]