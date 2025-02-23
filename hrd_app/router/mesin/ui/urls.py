from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('amesin/', views.amesin, name='amesin'),
    path('admesin/<int:id>', views.admesin, name='admesin'),
    path('rmesin/<int:userid>/<int:id>/<int:uid>', views.rmesin, name='rmesin'),
    path("datamesin/",views.datamesin,name="datamesin"),
    path("cdatamesin/",views.cdatamesin,name="cdatamesin"),
    path("listdata/",views.listdata,name="listdata"),
    path("testmesin/",views.testmesin,name="testmesin"),
    path("sinkron/",views.sinkrondatamemsin,name="sinkron"),
    # path("setuserid/<int:sid>",views.setuserid,name="setuserid"),
    # path("senddata/<int:sid>",views.senddata,name="senddata"),
    # path("auto",views.auto,name="auto"),
    # path("setnew",views.sin,name="setnew"),
    path("bynama/<str:nama>",views.bynama,name="bynama"),

    # path('cobas', views.haha, name='haha'),
]