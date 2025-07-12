from django.urls import path
from . import views

urlpatterns = [
    path("", views.OrderCreateAPIView.as_view()),
    path("<int:pk>/", views.OrderRetrieveAPIView.as_view()),
    path("cancel/<int:pk>/", views.CancelOrderAPIView.as_view()),
]
