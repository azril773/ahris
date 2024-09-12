from django.urls import path
from hrd_app.controllers import views



urlpatterns = [
    path('opg/<int:sid>', views.opg, name='opg'),
    path('copg', views.cari_opg, name='copg'),
    path('copg_s/<str:dr>/<str:sp>/<int:sid>', views.cari_opg_sid, name='copg_s'),
]