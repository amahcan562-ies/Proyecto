from rest_framework import serializers

from .models import ActivityRecord, PhysicalActivity


class PhysicalActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalActivity
        fields = [
            "id",
            "name",
            "met_value",
            "intensity",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El nombre de la actividad es obligatorio.")
        return value


class ActivityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRecord
        fields = [
            "id",
            "daily_record",
            "activity",
            "duration_min",
            "calories_burned_estimated",
            "performed_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_daily_record(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated and value.user_id != request.user.id:
            raise serializers.ValidationError(
                "No puedes registrar actividad en el diario de otro usuario."
            )
        return value

    def validate_activity(self, value):
        if not value.is_active:
            raise serializers.ValidationError("No puedes usar una actividad inactiva.")
        return value

    def validate_notes(self, value):
        return value.strip()

