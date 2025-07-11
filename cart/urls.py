from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartListAPIView.as_view(), name='list'),
]