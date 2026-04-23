from datetime import date

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "birth_date",
            "sex",
            "height_cm",
            "weight_kg",
            "target_weight_kg",
            "goal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def validate_birth_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        return value

    def validate(self, attrs):
        goal = attrs.get("goal", getattr(self.instance, "goal", Profile.GoalChoices.MAINTAIN))
        weight = attrs.get("weight_kg", getattr(self.instance, "weight_kg", None))
        target_weight = attrs.get(
            "target_weight_kg", getattr(self.instance, "target_weight_kg", None)
        )

        if goal != Profile.GoalChoices.MAINTAIN and target_weight is None:
            raise serializers.ValidationError(
                {"target_weight_kg": "Debes indicar un peso objetivo para este objetivo."}
            )

        if goal == Profile.GoalChoices.LOSE and weight and target_weight and target_weight >= weight:
            raise serializers.ValidationError(
                {"target_weight_kg": "Para perder peso, el objetivo debe ser menor al peso actual."}
            )

        if goal == Profile.GoalChoices.GAIN and weight and target_weight and target_weight <= weight:
            raise serializers.ValidationError(
                {"target_weight_kg": "Para ganar peso, el objetivo debe ser mayor al peso actual."}
            )

        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            RefreshToken(value)
        except TokenError as exc:
            raise serializers.ValidationError("Refresh token invalido o expirado.") from exc
        return value

    def save(self, **kwargs):
        refresh_token = self.validated_data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()


