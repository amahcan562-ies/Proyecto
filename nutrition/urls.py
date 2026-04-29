from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FoodConsumptionViewSet, FoodViewSet

app_name = "nutrition"

router = DefaultRouter()
router.register(r"foods", FoodViewSet, basename="food")
router.register(r"food-consumptions", FoodConsumptionViewSet, basename="food-consumption")

urlpatterns = [
    path("", include(router.urls)),
]
