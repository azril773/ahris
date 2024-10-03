from django.urls import path
from hrd_app.controllers import views

urlpatterns = [
    path('prodemo/<int:idp>', views.promosi_demosi, name='prodemo'),
    path('prodemo_nonaktif/<int:idp>', views.promosi_demosi_nonaktif, name='prodemo_nonaktif'),
]