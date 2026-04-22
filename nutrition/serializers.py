from decimal import Decimal

from rest_framework import serializers

from .models import Food, FoodConsumption


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = [
            "id",
            "name",
            "brand",
            "calories_per_100g",
            "protein_per_100g",
            "carbs_per_100g",
            "fat_per_100g",
            "fiber_per_100g",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El nombre del alimento es obligatorio.")
        return value

    def validate_brand(self, value):
        return value.strip()

    def validate(self, attrs):
        protein = attrs.get("protein_per_100g", getattr(self.instance, "protein_per_100g", Decimal("0")))
        carbs = attrs.get("carbs_per_100g", getattr(self.instance, "carbs_per_100g", Decimal("0")))
        fat = attrs.get("fat_per_100g", getattr(self.instance, "fat_per_100g", Decimal("0")))
        fiber = attrs.get("fiber_per_100g", getattr(self.instance, "fiber_per_100g", Decimal("0")))

        total = protein + carbs + fat + fiber
        if total > Decimal("100"):
            raise serializers.ValidationError(
                "La suma de macronutrientes y fibra no puede superar 100 g por cada 100 g."
            )

        return attrs


class FoodConsumptionSerializer(serializers.ModelSerializer):
    amount_g = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=Decimal("5000"),
    )

    class Meta:
        model = FoodConsumption
        fields = [
            "id",
            "daily_record",
            "food",
            "amount_g",
            "meal_type",
            "consumed_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_daily_record(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated and value.user_id != request.user.id:
            raise serializers.ValidationError(
                "No puedes registrar alimentos en el diario de otro usuario."
            )
        return value

    def validate_food(self, value):
        if not value.is_active:
            raise serializers.ValidationError("No puedes usar un alimento inactivo.")
        return value

    def validate_notes(self, value):
        return value.strip()
