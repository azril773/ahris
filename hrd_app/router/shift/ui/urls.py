from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path("shift",views.shift,name="shift"),
]