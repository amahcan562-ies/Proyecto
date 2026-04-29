from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DailyEvaluationViewSet, DailyRecordViewSet

app_name = "evaluations"

router = DefaultRouter()
router.register(r"daily-records", DailyRecordViewSet, basename="daily-record")
router.register(r"daily-evaluations", DailyEvaluationViewSet, basename="daily-evaluation")

urlpatterns = [
    path("", include(router.urls)),
]
