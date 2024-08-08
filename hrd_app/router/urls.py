from django.urls import path
from hrd_app import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('logindispatch', views.logindispatch, name='dispatch'),
    path('login', auth_views.LoginView.as_view(template_name='hrd_app/login.html'), name='login'),
    path('logout', views.user_logout, name='logout'),
    
    path('', views.beranda, name='beranda'), 
    path('noakses', views.beranda_no_akses, name='noakses'), 
]