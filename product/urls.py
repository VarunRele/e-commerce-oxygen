from django.urls import path
from . import views

urlpatterns = [
    path("", views.ProductListCreateAPIView.as_view(), name="list-create"),
    path("<int:pk>/", views.ProductDetailAPIView.as_view(), name="product"),
]