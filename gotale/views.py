from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.request import Request
from gotale.serializers import (
    UserSerializer,
    LocationSerializer,
    ScenarioSerializer,
    StepSerializer,
    GameSerializer,
)
from rest_framework import viewsets
from gotale.models import Location, Scenario, Step, Game
from rest_framework.decorators import action


# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    # TODO: user should be able to update only own profile
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        methods=["GET", "PUT", "PATCH"],
        permission_classes=[permissions.IsAuthenticated],
        url_name="current",
        url_path="me",
        name="Current User",
    )
    def current_user(self, request: Request) -> Response:
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(user)

        return Response(serializer.errors)


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
    # TODO: GET /step action for current game /api/game/:id/step
    # TODO: POST /step action for current game decision
    queryset = Game.objects.all()
    serializer_class = GameSerializer
