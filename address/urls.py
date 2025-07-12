from django.urls import path
from . import views

urlpatterns = [
    path("", views.AddressListCreateAPIView.as_view()),
    path("<int:pk>/", views.AddressRetriveUpdateDestroyAPIView.as_view())
]
