from django.urls import path
from . import views

urlpatterns = [
    path("", views.OrderCreateAPIView.as_view()),
    path("<int:pk>/", views.OrderRetrieveAPIView.as_view()),
    path("cancel/<int:pk>/", views.CancelOrderAPIView.as_view()),
    path("payment/<int:pk>/", views.CreateRazorPayOrderAPIView.as_view()),
    path("payment/verify/", views.VerifyRazorPayPaymentAPIView.as_view())
]
