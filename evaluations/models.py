from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class DailyRecord(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="daily_records",
	)
	date = models.DateField(default=timezone.localdate)
	water_intake_ml = models.PositiveIntegerField(
		blank=True,
		null=True,
		validators=[MinValueValidator(0), MaxValueValidator(15000)],
	)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date"]
		constraints = [
			models.UniqueConstraint(
				fields=["user", "date"],
				name="daily_record_unique_user_date",
			)
		]
		indexes = [
			models.Index(fields=["user", "date"]),
			models.Index(fields=["date"]),
		]

	def __str__(self) -> str:
		return f"{self.user.username} - {self.date}"


class DailyEvaluation(models.Model):
	daily_record = models.OneToOneField(
		DailyRecord,
		on_delete=models.CASCADE,
		related_name="evaluation",
	)
	score = models.PositiveSmallIntegerField(
		validators=[MinValueValidator(0), MaxValueValidator(100)]
	)
	recommendations = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-daily_record__date"]

	def __str__(self) -> str:
		return f"Evaluacion {self.daily_record.date}: {self.score}/100"
