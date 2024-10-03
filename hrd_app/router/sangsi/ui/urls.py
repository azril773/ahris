from django.urls import path
from hrd_app.controllers import views


urlpatterns = [
    path('sangsi/<int:idp>', views.sangsi, name='sangsi'),
    path('sangsi_nonaktif/<int:idp>', views.sangsi_nonaktif, name='sangsi_nonaktif'),
]