from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('sangsi/<int:idp>', views.sangsi, name='sangsi'),
]