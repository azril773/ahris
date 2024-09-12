from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('cuti/<int:sid>', views.cuti, name='cuti'),
    path('cuti/<int:sid>/<int:idp>', views.detail_cuti, name='dcuti'),   
    path('ccuti', views.cari_cuti, name='ccuti'),
    
]