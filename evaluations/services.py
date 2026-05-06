from decimal import Decimal, ROUND_HALF_UP

from activity.models import ActivityRecord
from nutrition.models import FoodConsumption
from users.models import Profile

from .models import DailyEvaluation

DEFAULT_CALORIE_GOAL = Decimal("2200")
DEFAULT_PROTEIN_GOAL = Decimal("120")
DEFAULT_CARBS_GOAL = Decimal("220")
DEFAULT_FAT_GOAL = Decimal("70")
DEFAULT_WEIGHT_KG = Decimal("70")
DEFAULT_WATER_GOAL_ML = 2000


def _as_decimal(value, default=Decimal("0")):
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def get_user_profile(user):
    if not user or not user.is_authenticated:
        return None
    return Profile.objects.filter(user=user).first()


def get_user_goals(user, profile=None):
    profile = profile or get_user_profile(user)
    if not profile or profile.weight_kg is None:
        return {
            "calories": DEFAULT_CALORIE_GOAL,
            "protein": DEFAULT_PROTEIN_GOAL,
            "carbs": DEFAULT_CARBS_GOAL,
            "fat": DEFAULT_FAT_GOAL,
            "water_ml": DEFAULT_WATER_GOAL_ML,
            "weight_kg": DEFAULT_WEIGHT_KG,
        }

    weight = _as_decimal(profile.weight_kg)
    calories_goal = weight * Decimal("30")
    if profile.goal == Profile.GoalChoices.LOSE:
        calories_goal -= Decimal("300")
    elif profile.goal == Profile.GoalChoices.GAIN:
        calories_goal += Decimal("300")

    calories_goal = max(Decimal("1200"), min(calories_goal, Decimal("4000")))

    protein_goal = weight * Decimal("1.6")
    fat_goal = weight * Decimal("0.8")
    remaining = calories_goal - (protein_goal * Decimal("4")) - (fat_goal * Decimal("9"))
    carbs_goal = max(Decimal("0"), remaining / Decimal("4"))

    return {
        "calories": calories_goal.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
        "protein": protein_goal.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
        "carbs": carbs_goal.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
        "fat": fat_goal.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP),
        "water_ml": DEFAULT_WATER_GOAL_ML,
        "weight_kg": weight,
    }


def estimate_activity_calories(activity, duration_min, weight_kg=None):
    if not activity or not duration_min:
        return 0
    weight = _as_decimal(weight_kg, DEFAULT_WEIGHT_KG)
    hours = _as_decimal(duration_min) / Decimal("60")
    calories = activity.met_value * weight * hours
    return int(calories.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calculate_daily_totals(daily_record):
    calories = Decimal("0")
    protein = Decimal("0")
    carbs = Decimal("0")
    fat = Decimal("0")

    consumptions = FoodConsumption.objects.filter(
        daily_record=daily_record
    ).select_related("food")
    for item in consumptions:
        factor = _as_decimal(item.amount_g) / Decimal("100")
        calories += factor * item.food.calories_per_100g
        protein += factor * item.food.protein_per_100g
        carbs += factor * item.food.carbs_per_100g
        fat += factor * item.food.fat_per_100g

    activity_calories = sum(
        record.calories_burned_estimated or 0
        for record in ActivityRecord.objects.filter(daily_record=daily_record)
    )

    return {
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "activity_calories": activity_calories,
        "water_ml": daily_record.water_intake_ml or 0,
    }


def _score_component(actual, goal):
    if goal <= 0:
        return 0
    ratio = abs(actual - goal) / goal
    ratio = min(ratio, 1)
    return int((Decimal("1") - ratio) * Decimal("100"))


def calculate_score(totals, goals):
    calories_score = _score_component(totals["calories"], goals["calories"])
    protein_score = _score_component(totals["protein"], goals["protein"])
    carbs_score = _score_component(totals["carbs"], goals["carbs"])
    fat_score = _score_component(totals["fat"], goals["fat"])
    score = (
        calories_score * 0.4
        + protein_score * 0.2
        + carbs_score * 0.2
        + fat_score * 0.2
    )
    return max(0, min(int(round(score)), 100))


def build_recommendations(totals, goals):
    recommendations = []

    if totals["calories"] > goals["calories"] * Decimal("1.1"):
        recommendations.append("Reduce calorias para equilibrar tu dia.")
    elif totals["calories"] < goals["calories"] * Decimal("0.8"):
        recommendations.append("Estas por debajo del objetivo calorico.")

    if totals["protein"] < goals["protein"] * Decimal("0.9"):
        recommendations.append("Aumenta proteina para alcanzar tu meta diaria.")

    if totals["carbs"] > goals["carbs"] * Decimal("1.1"):
        recommendations.append("Modera los carbohidratos para mantener el balance.")

    if totals["fat"] > goals["fat"] * Decimal("1.1"):
        recommendations.append("Reduce grasas para ajustar tu objetivo.")

    if totals["water_ml"] and totals["water_ml"] < goals["water_ml"]:
        recommendations.append("Hidratate con al menos 2 vasos mas.")

    if not recommendations:
        recommendations.append("Buen trabajo, mantienes el ritmo.")

    return recommendations[:3]


def ensure_daily_evaluation(daily_record, totals=None, goals=None):
    goals = goals or get_user_goals(daily_record.user)
    totals = totals or calculate_daily_totals(daily_record)
    score = calculate_score(totals, goals)
    recommendations = build_recommendations(totals, goals)

    evaluation, _ = DailyEvaluation.objects.update_or_create(
        daily_record=daily_record,
        defaults={
            "score": score,
            "recommendations": "\n".join(recommendations),
        },
    )

    return evaluation, totals, goals, recommendations

