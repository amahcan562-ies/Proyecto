from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsDailyRecordOwner, IsStaffOrReadOnly
from .models import Food, FoodConsumption
from .serializers import FoodConsumptionSerializer, FoodSerializer


class FoodViewSet(ModelViewSet):
    serializer_class = FoodSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = Food.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by("name", "brand")


class FoodConsumptionViewSet(ModelViewSet):
    serializer_class = FoodConsumptionSerializer
    permission_classes = [IsAuthenticated, IsDailyRecordOwner]

    def get_queryset(self):
        return (
            FoodConsumption.objects.select_related("daily_record", "food")
            .filter(daily_record__user=self.request.user)
            .order_by("-created_at")
        )
