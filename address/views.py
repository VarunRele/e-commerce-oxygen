from django.shortcuts import render
from .models import Address
from .serializers import AddressSerializer
from rest_framework import generics, authentication, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.permission import IsOwnerOrAdmin


class AddressListCreateAPIView(generics.ListCreateAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Address.objects.all()
        return Address.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressRetriveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    authentication_classes = [authentication.SessionAuthentication, JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]