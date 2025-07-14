from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartListAPIView.as_view(), name='list'),
    path("add/", views.CartItemCreateAPIView.as_view(), name='add-item'),
    path("increment/<int:pk>/", views.CartItemIncrementAPIView.as_view(), name='increment-cartitem'),
    path("decrement/<int:pk>/", views.CartItemDecrementAPIView.as_view(), name='decrement-cartitem'),
    path("delete/<int:pk>/", views.CartItemDestoryAPIView.as_view())
]