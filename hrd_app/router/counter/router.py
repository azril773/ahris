from django.urls import path
from hrd_app import views

urlsAjaxCounter = [
    path('counter_json', views.counter_json, name='counter_json'),
    path('tcounter', views.tambah_counter, name='tcounter'),
    path('ecounter', views.edit_counter, name='ecounter'),
    path('hcounter', views.hapus_counter, name='hcounter'),
]

urlsRenderCounter = [
    path('counter', views.counter, name='counter'),
]