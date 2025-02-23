from rest_framework import routers
from gotale.views import UserViewset, LocationViewset, ScenarioViewset

router = routers.DefaultRouter()
router.register("users", UserViewset, basename="user")
router.register("locations", LocationViewset, basename="location")
router.register("scenarios", ScenarioViewset, basename="scenario")

urlpatterns = router.urls
