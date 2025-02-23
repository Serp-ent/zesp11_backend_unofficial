from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.response import Response
from datetime import timezone
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from gotale.serializers import (
    UserSerializer,
    LocationSerializer,
    ScenarioSerializer,
    StepSerializer,
    GameSerializer,
    MakeChoiceSerializer,
)
from rest_framework import viewsets
from gotale.models import Location, Scenario, Step, Game, History, Choice, Session
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

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(user)


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

    @action(
        detail=True,
        methods=["GET", "POST"],
        url_name="current-step",
        url_path="step",
        name="Current game step",
    )
    def current_step(self, request: Request, pk=None) -> Response:
        # TODO: permissions
        game = self.get_object()
        if request.method == "GET":
            step = game.current_step
            serializer = StepSerializer(step)
            return Response(serializer.data)

        # POST METHDO
        if game.status == "ended":
            return Response(
                {"error": "This game has already ended"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MakeChoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        choice_id = serializer.validated_data["choice_id"]

        try:
            choice = game.current_step.choices.get(id=choice_id)
        except Choice.DoesNotExist:
            return Response(
                {"errors": "Invalid choice ID for current step"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get active session
        try:
            session = game.sessions.filter(is_active=True).get()
        except Session.DoesNotExist:
            return Response(
                {"error": "No active session found"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Update game state
        original_step = game.current_step
        game.current_step = choice.next

        if game.current_step.is_last_step():
            game.end = timezone.now()

        game.save()

        # Record history
        History.objects.create(
            session=session,
            choice=choice,
            step=original_step,
        )

        return Response(
            StepSerializer(game.current_step).data,
            status=status.HTTP_200_OK,
        )
