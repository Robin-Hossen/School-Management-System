from rest_framework import serializers
from .models import CustomUser

class RegistrationSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,required=True,min_length=8)

    class Meta:
        model=CustomUser
        fields=['email','password','first_name','last_name']

    def create(self,validated_data): #CustomUser ar password directly save korte parbe na, tai amra create method override kore password ke hash kore save korbo
        password=validated_data.pop('password')
        user=CustomUser.objects.create_user(password=password,**validated_data)
        return user

class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['id','email','first_name','last_name']    
        read_only_fields=['id','email'] #profile view te user email, first_name, last_name change korte parbe na, tai read_only_fields use korbo


class LogoutSerializer(serializers.Serializer):
    refresh= serializers.CharField(required=True)