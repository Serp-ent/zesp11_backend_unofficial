from django.shortcuts import render
from django.contrib.auth.models import User
from gotale.serializers import (
    UserSerializer,
    LocationSerializer,
    ScenarioSerializer,
    StepSerializer,
    GameSerializer,
)
from rest_framework import viewsets
from gotale.models import Location, Scenario, Step, Game


# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class LocationViewset(viewsets.ModelViewSet):
    # TODO: only admin should be able to create/update/destroy locations
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class ScenarioViewset(viewsets.ModelViewSet):
    # TODO: everyone can create scenarios
    # TODO: only owner/admin can update/destroy scenario
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer


class StepsViewset(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer


class GameViewsets(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
