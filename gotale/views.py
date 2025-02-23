from django.shortcuts import render
from django.contrib.auth.models import User
from gotale.serializers import UserSerializer
from rest_framework import viewsets


# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
