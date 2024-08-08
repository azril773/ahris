from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('adminnya/', admin.site.urls),
    path('', auth_views.LoginView.as_view(template_name='hrd_app/login.html'), name='login'),

    path('hrd', include('hrd_app.router.urls')),
]
