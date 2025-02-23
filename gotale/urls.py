from rest_framework import routers
from gotale.views import (
    UserViewset,
    LocationViewset,
    ScenarioViewset,
    StepsViewset,
    GameViewsets,
    RegisterView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include

router = routers.DefaultRouter()
router.register("users", UserViewset, basename="user")
router.register("locations", LocationViewset, basename="location")
router.register("scenarios", ScenarioViewset, basename="scenario")
router.register("games", GameViewsets, basename="game")

# TODO: /api/auth/register
# TODO: /api/auth/login
# TODO: /api/auth/logout
# TODO: /api/auth/refresh


urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
]

urlpatterns += router.urls
