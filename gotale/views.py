from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from datetime import timezone, datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework import permissions
from gotale import permissions as gotalePermissions
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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [gotalePermissions.UserPermission]

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

        partial = request.method == "PATCH"
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LocationViewset(viewsets.ModelViewSet):
    permission_classes = [gotalePermissions.IsAdminOrReadOnly]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class ScenarioViewset(viewsets.ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]

        return [gotalePermissions.IsOwnerOrAdminOrReadOnly()]


class GameViewsets(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [gotalePermissions.isAuthenticatedOrAdmin]

    def get_permissions(self):
        if self.action in ["current_step", "end_session"]:
            return [gotalePermissions.IsInGame()]

        return super().get_permissions()

    def perform_create(self, serializer):
        """Auto-create first session on game creation"""
        game = serializer.save(user=self.request.user)

        Session.objects.create(game=game, is_active=True)

        return game

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

        active_session = game.sessions.filter(is_active=True).first()
        if not active_session:
            active_session = Session.objects.create(game=game, is_active=True)

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

        # Update game state
        original_step = game.current_step
        game.current_step = choice.next

        if game.current_step.is_last_step():
            game.end = datetime.now()

        game.save()

        # Record history
        History.objects.create(
            session=active_session,
            choice=choice,
            step=original_step,
        )

        return Response(
            StepSerializer(game.current_step).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["POST"],
        url_path="end-session",
        url_name="session-end",
        name="End session for current game",
    )
    def end_session(self, request, pk=None):
        """Frontend needs to call this when leaving"""
        game = self.get_object()
        session = game.sessions.filter(is_active=True).first()

        if session:
            session.is_active = False
            session.end = datetime.now()
            session.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save

        # Generate tokens for immediate login
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )
