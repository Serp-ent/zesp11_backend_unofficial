from django.contrib.auth.models import User
from rest_framework import serializers
from gotale.models import Location


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "date_joined"]

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['name', 'longitude', 'latitude']
