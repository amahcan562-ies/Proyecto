from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Food(models.Model):
	name = models.CharField(max_length=120, db_index=True)
	brand = models.CharField(max_length=120, blank=True)
	calories_per_100g = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		validators=[MinValueValidator(0), MaxValueValidator(900)],
	)
	protein_per_100g = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
	)
	carbs_per_100g = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
	)
	fat_per_100g = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
	)
	fiber_per_100g = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
		default=0,
	)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name", "brand"]
		constraints = [
			models.CheckConstraint(
				condition=Q(calories_per_100g__gte=0),
				name="food_calories_non_negative",
			),
			models.CheckConstraint(
				condition=Q(protein_per_100g__gte=0),
				name="food_protein_non_negative",
			),
			models.CheckConstraint(
				condition=Q(carbs_per_100g__gte=0),
				name="food_carbs_non_negative",
			),
			models.CheckConstraint(
				condition=Q(fat_per_100g__gte=0),
				name="food_fat_non_negative",
			),
			models.CheckConstraint(
				condition=Q(fiber_per_100g__gte=0),
				name="food_fiber_non_negative",
			),
			models.UniqueConstraint(
				fields=["name", "brand"],
				name="food_unique_name_brand",
			),
		]

	def __str__(self) -> str:
		label = self.name
		if self.brand:
			label = f"{label} ({self.brand})"
		return label


class FoodConsumption(models.Model):
	class MealChoices(models.TextChoices):
		BREAKFAST = "BREAKFAST", "Desayuno"
		LUNCH = "LUNCH", "Comida"
		DINNER = "DINNER", "Cena"
		SNACK = "SNACK", "Snack"

	daily_record = models.ForeignKey(
		"evaluations.DailyRecord",
		on_delete=models.CASCADE,
		related_name="food_consumptions",
	)
	food = models.ForeignKey(
		Food,
		on_delete=models.PROTECT,
		related_name="consumptions",
	)
	amount_g = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		validators=[MinValueValidator(0.01), MaxValueValidator(5000)],
	)
	meal_type = models.CharField(
		max_length=12,
		choices=MealChoices.choices,
		default=MealChoices.LUNCH,
	)
	consumed_at = models.TimeField(blank=True, null=True)
	notes = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["daily_record", "meal_type"]),
			models.Index(fields=["food"]),
		]

	def __str__(self) -> str:
		return f"{self.food.name} - {self.amount_g} g"
