from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.serializers import (
    UserRegisterSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from gotale import permissions as gotalePermissions
from gotale.models import Choice, Game, History, Location, Scenario, Session
from gotale.serializers import (
    GameCreateSerializer,
    GameSerializer,
    LocationSerializer,
    MakeChoiceSerializer,
    ScenarioCreateSerializer,
    ScenarioSerializer,
    StepSerializer,
)

User = get_user_model()


# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # TODO:
    # permission_classes = [gotalePermissions.UserPermission]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

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

    serializer_class_by_action = {
        "create": ScenarioCreateSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_class_by_action.get(self.action, ScenarioSerializer)

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]

        return [gotalePermissions.IsOwnerOrAdminOrReadOnly()]

    def create(self, request, *args, **kwargs):
        serializer_create = self.get_serializer(data=request.data)
        serializer_create.is_valid(raise_exception=True)

        instance = self.perform_create(serializer_create)

        return Response(
            ScenarioSerializer(instance, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class GameViewsets(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [gotalePermissions.isAuthenticatedOrAdmin]
    serializers_by_action = {
        "create": GameCreateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers_by_action.get(self.action, GameSerializer)

    def get_permissions(self):
        if self.action in ["current_step", "end_session"]:
            return [gotalePermissions.IsInGame()]

        return super().get_permissions()

    def perform_create(self, serializer):
        """Auto-create first session on game creation"""
        game = serializer.save(user=self.request.user)
        game.current_step = game.scenario.root_step
        game.save()

        # Session.objects.create(game=game, is_active=True)

        return game

    def create(self, request, *args, **kwargs):
        serializer_create = self.get_serializer(data=request.data)
        serializer_create.is_valid(raise_exception=True)

        self.perform_create(serializer_create)

        instance = serializer_create.instance
        return Response(
            GameSerializer(instance, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
        )

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
            serializer = StepSerializer(game.current_step)
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
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )
