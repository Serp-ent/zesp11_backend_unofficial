from django.shortcuts import render
from django.contrib.auth.models import User
from gotale.serializers import UserSerializer, LocationSerializer
from rest_framework import viewsets
from gotale.models import Location


# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LocationViewset(viewsets.ModelViewSet):
    # TODO: only admin should be able to create/update/destroy locations
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
