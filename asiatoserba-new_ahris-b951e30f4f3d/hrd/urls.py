from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('adminnya/', admin.site.urls),
    path('hrd/',include('hrd_app.urls')),
    path('', auth_views.LoginView.as_view(template_name='hrd_app/login.html'), name='login'),
]
