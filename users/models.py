from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Profile(models.Model):
	class SexChoices(models.TextChoices):
		MALE = "M", "Hombre"
		FEMALE = "F", "Mujer"
		UNSPECIFIED = "U", "No especificado"

	class GoalChoices(models.TextChoices):
		LOSE = "LOSE", "Perder peso"
		MAINTAIN = "MAINTAIN", "Mantener peso"
		GAIN = "GAIN", "Ganar peso"

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="profile",
	)
	birth_date = models.DateField(blank=True, null=True)
	sex = models.CharField(
		max_length=1,
		choices=SexChoices.choices,
		default=SexChoices.UNSPECIFIED,
	)
	height_cm = models.PositiveSmallIntegerField(
		blank=True,
		null=True,
		validators=[MinValueValidator(80), MaxValueValidator(250)],
	)
	weight_kg = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		blank=True,
		null=True,
		validators=[MinValueValidator(20), MaxValueValidator(400)],
	)
	target_weight_kg = models.DecimalField(
		max_digits=5,
		decimal_places=2,
		blank=True,
		null=True,
		validators=[MinValueValidator(20), MaxValueValidator(400)],
	)
	goal = models.CharField(
		max_length=10,
		choices=GoalChoices.choices,
		default=GoalChoices.MAINTAIN,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["user_id"]

	def __str__(self) -> str:
		return f"Perfil de {self.user.username}"
