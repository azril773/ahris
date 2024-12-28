from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('amesin/', views.amesin, name='amesin'),
    path('admesin/<int:id>', views.admesin, name='admesin'),
    path('rmesin/<int:userid>/<int:id>/<int:uid>', views.rmesin, name='rmesin'),
    path("datamesin/",views.datamesin,name="datamesin"),
    path("cdatamesin/",views.cdatamesin,name="cdatamesin"),
    path("listdata/",views.listdata,name="listdata"),
]