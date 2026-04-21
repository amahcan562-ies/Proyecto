from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class PhysicalActivity(models.Model):
	class IntensityChoices(models.TextChoices):
		LOW = "LOW", "Baja"
		MODERATE = "MODERATE", "Moderada"
		HIGH = "HIGH", "Alta"

	name = models.CharField(max_length=120, unique=True)
	met_value = models.DecimalField(
		max_digits=4,
		decimal_places=2,
		validators=[MinValueValidator(0.5), MaxValueValidator(25)],
	)
	intensity = models.CharField(
		max_length=10,
		choices=IntensityChoices.choices,
		default=IntensityChoices.MODERATE,
	)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["name"]

	def __str__(self) -> str:
		return self.name


class ActivityRecord(models.Model):
	daily_record = models.ForeignKey(
		"evaluations.DailyRecord",
		on_delete=models.CASCADE,
		related_name="activity_records",
	)
	activity = models.ForeignKey(
		PhysicalActivity,
		on_delete=models.PROTECT,
		related_name="records",
	)
	duration_min = models.PositiveIntegerField(
		validators=[MinValueValidator(1), MaxValueValidator(1440)]
	)
	calories_burned_estimated = models.PositiveIntegerField(blank=True, null=True)
	performed_at = models.TimeField(blank=True, null=True)
	notes = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]
		indexes = [
			models.Index(fields=["daily_record", "activity"]),
			models.Index(fields=["activity"]),
		]
		constraints = [
			models.CheckConstraint(
				condition=Q(calories_burned_estimated__gte=0)
				| Q(calories_burned_estimated__isnull=True),
				name="activity_record_calories_non_negative",
			)
		]

	def __str__(self) -> str:
		return f"{self.activity.name} - {self.duration_min} min"
