from rest_framework import routers
from gotale.views import UserViewset, LocationViewset

router = routers.DefaultRouter()
router.register("users", UserViewset, basename="user")
router.register('locations', LocationViewset, basename='location')

urlpatterns = router.urls
