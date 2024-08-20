from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('counter_json', views.counter_json, name='counter_json'),
    path('tcounter', views.tambah_counter, name='tcounter'),
    path('ecounter', views.edit_counter, name='ecounter'),
    path('hcounter', views.hapus_counter, name='hcounter'),
]
