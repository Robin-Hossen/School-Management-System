from django.shortcuts import render
from rest_framework import generics
from .serializers import ProfileSerializers, RegistrationSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdmin,IsTeacher,IsStudent,IsParent,IsAccountant
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    ProfileSerializers,
    RegistrationSerializer,
    LogoutSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
)

# Create your views here.

class RegisterView(generics.CreateAPIView):
    serializer_class=RegistrationSerializer
    permission_classes=[AllowAny] #login ba token na thakleo register korte parbe, tai amra AllowAny permission use korbo



class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class=ProfileSerializers
    permission_classes=[IsAuthenticated] #login thakle profile dekhte parbe,

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.get_serializer(
            data=request.data,
            context={
                "request": request
            }
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "detail": "Password changed successfully."
            },
            status=status.HTTP_200_OK
        )

#LogoutView
class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self,request):
        serializer=LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token=serializer.validated_data["refresh"]

        try:
            
            token=RefreshToken(refresh_token)
            token.blacklist() #blacklist the refresh token
            return Response({"detail":"Logout successful"},status=status.HTTP_205_RESET_CONTENT) 
        
        except Exception:
            return Response({"detail":"Invalid or expired refresh token"},status=status.HTTP_400_BAD_REQUEST) 


class AdminTestView(APIView):
    permission_classes=[IsAuthenticated,IsAdmin]

    def get(self,request):
        return Response({"message":"Welcome Admin!",
                        "user":request.user.email,
                        "role":request.user.role})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer    


