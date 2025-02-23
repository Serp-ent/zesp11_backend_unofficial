from rest_framework import routers
from gotale.views import UserViewset, LocationViewset, ScenarioViewset, StepsViewset, GameViewsets

router = routers.DefaultRouter()
router.register("users", UserViewset, basename="user")
router.register("locations", LocationViewset, basename="location")
router.register("scenarios", ScenarioViewset, basename="scenario")
router.register("steps", StepsViewset, basename="step")
router.register("games", GameViewsets, basename="game")

urlpatterns = router.urls
