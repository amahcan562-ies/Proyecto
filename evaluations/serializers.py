from django.utils import timezone
from rest_framework import serializers

from .models import DailyEvaluation, DailyRecord


class DailyRecordSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = DailyRecord
        fields = [
            "id",
            "user",
            "date",
            "water_intake_ml",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("No se permiten registros en fechas futuras.")
        return value


class DailyEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyEvaluation
        fields = [
            "id",
            "daily_record",
            "score",
            "recommendations",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_daily_record(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated and value.user_id != request.user.id:
            raise serializers.ValidationError(
                "No puedes evaluar un registro diario de otro usuario."
            )
        return value

    def validate(self, attrs):
        daily_record = attrs.get("daily_record", getattr(self.instance, "daily_record", None))
        if daily_record and hasattr(daily_record, "evaluation"):
            if not self.instance or daily_record.evaluation_id != self.instance.id:
                raise serializers.ValidationError(
                    {"daily_record": "Este registro diario ya tiene una evaluacion."}
                )
        return attrs

