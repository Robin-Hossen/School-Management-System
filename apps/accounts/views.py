from django.shortcuts import render
from rest_framework import generics
from .serializers import ProfileSerializers, RegistrationSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated


# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class=RegistrationSerializer
    permission_classes=[AllowAny] #login ba token na thakleo register korte parbe, tai amra AllowAny permission use korbo

class ProfileView(generics.RetrieveAPIView):
    serializer_class=ProfileSerializers
    permission_classes=[IsAuthenticated] #login thakle profile dekhte parbe,

    def get_object(self):
        return self.request.user