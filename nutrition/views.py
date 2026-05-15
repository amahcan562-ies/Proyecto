from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsDailyRecordOwner, IsStaffOrReadOnly
from evaluations.services import ensure_daily_evaluation
from .models import Food, FoodConsumption
from .serializers import FoodConsumptionSerializer, FoodSerializer


class FoodViewSet(ModelViewSet):
    serializer_class = FoodSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = Food.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        query = self.request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(brand__icontains=query))

        queryset = queryset.order_by("name", "brand")
        limit = self.request.query_params.get("limit", "").strip()
        if limit.isdigit():
            queryset = queryset[: min(int(limit), 100)]
        return queryset


class FoodConsumptionViewSet(ModelViewSet):
    serializer_class = FoodConsumptionSerializer
    permission_classes = [IsAuthenticated, IsDailyRecordOwner]

    def get_queryset(self):
        return (
            FoodConsumption.objects.select_related("daily_record", "food")
            .filter(daily_record__user=self.request.user)
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        ensure_daily_evaluation(instance.daily_record)

    def perform_update(self, serializer):
        instance = serializer.save()
        ensure_daily_evaluation(instance.daily_record)

    def perform_destroy(self, instance):
        daily_record = instance.daily_record
        instance.delete()
        ensure_daily_evaluation(daily_record)
