from decimal import Decimal

from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView

from activity.models import ActivityRecord, PhysicalActivity
from evaluations.models import DailyEvaluation, DailyRecord
from nutrition.models import Food, FoodConsumption
from users.models import Profile

from .forms import ActivityRecordForm, FoodConsumptionForm, ProfileForm


DEFAULT_CALORIE_GOAL = Decimal("2200")
DEFAULT_PROTEIN_GOAL = Decimal("120")
DEFAULT_CARBS_GOAL = Decimal("220")
DEFAULT_FAT_GOAL = Decimal("70")


def _percentage(value: Decimal, goal: Decimal) -> int:
    if goal <= 0:
        return 0
    return min(int((value / goal) * 100), 100)


def _build_today_context(user):
    today = timezone.localdate()
    context = {
        "is_authenticated": user.is_authenticated,
        "today": today,
        "daily_record": None,
        "calories_consumed": Decimal("0"),
        "calories_goal": DEFAULT_CALORIE_GOAL,
        "calories_remaining": DEFAULT_CALORIE_GOAL,
        "calories_percent": 0,
        "protein_total": Decimal("0"),
        "protein_goal": DEFAULT_PROTEIN_GOAL,
        "protein_percent": 0,
        "carbs_total": Decimal("0"),
        "carbs_goal": DEFAULT_CARBS_GOAL,
        "carbs_percent": 0,
        "fat_total": Decimal("0"),
        "fat_goal": DEFAULT_FAT_GOAL,
        "fat_percent": 0,
        "activity_calories": 0,
        "score": 0,
        "recommendations": [
            "Aumenta proteina para alcanzar tu meta diaria.",
            "Buen trabajo, mantienes el ritmo.",
            "Hidratate con al menos 2 vasos mas.",
        ],
        "meals_today": [],
        "activities_today": [],
    }

    if not user.is_authenticated:
        return context

    daily_record, _ = DailyRecord.objects.get_or_create(user=user, date=today)
    consumption_qs = FoodConsumption.objects.filter(
        daily_record=daily_record
    ).select_related("food")
    activity_qs = ActivityRecord.objects.filter(
        daily_record=daily_record
    ).select_related("activity")

    calories = Decimal("0")
    protein = Decimal("0")
    carbs = Decimal("0")
    fat = Decimal("0")

    for item in consumption_qs:
        factor = item.amount_g / Decimal("100")
        calories += factor * item.food.calories_per_100g
        protein += factor * item.food.protein_per_100g
        carbs += factor * item.food.carbs_per_100g
        fat += factor * item.food.fat_per_100g

    activity_calories = sum(
        record.calories_burned_estimated or 0 for record in activity_qs
    )

    evaluation = DailyEvaluation.objects.filter(daily_record=daily_record).first()
    recommendations = []
    if evaluation and evaluation.recommendations:
        recommendations = [
            line.strip()
            for line in evaluation.recommendations.splitlines()
            if line.strip()
        ]

    if not recommendations:
        recommendations = context["recommendations"]

    calories_remaining = max(DEFAULT_CALORIE_GOAL - calories, Decimal("0"))

    context.update(
        {
            "daily_record": daily_record,
            "calories_consumed": calories,
            "calories_remaining": calories_remaining,
            "calories_percent": _percentage(calories, DEFAULT_CALORIE_GOAL),
            "protein_total": protein,
            "protein_percent": _percentage(protein, DEFAULT_PROTEIN_GOAL),
            "carbs_total": carbs,
            "carbs_percent": _percentage(carbs, DEFAULT_CARBS_GOAL),
            "fat_total": fat,
            "fat_percent": _percentage(fat, DEFAULT_FAT_GOAL),
            "activity_calories": activity_calories,
            "score": evaluation.score if evaluation else 0,
            "recommendations": recommendations,
            "meals_today": list(consumption_qs[:6]),
            "activities_today": list(activity_qs[:6]),
        }
    )

    return context



class DashboardView(TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_build_today_context(self.request.user))
        context.update({"active_nav": "dashboard"})
        return context


class AddFoodView(View):
    template_name = "core/add_food.html"

    def get(self, request):
        context = _build_today_context(request.user)
        context.update(
            {
                "active_nav": "add_food",
                "form": FoodConsumptionForm(),
                "foods": Food.objects.filter(is_active=True)[:20],
                "consumptions": (
                    FoodConsumption.objects.filter(daily_record=context["daily_record"]).select_related("food")
                    if request.user.is_authenticated
                    else []
                ),
            }
        )
        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.is_authenticated:
            context = _build_today_context(request.user)
            context.update(
                {
                    "active_nav": "add_food",
                    "form": FoodConsumptionForm(request.POST),
                    "form_error": "Necesitas iniciar sesion para registrar alimentos.",
                    "foods": Food.objects.filter(is_active=True)[:20],
                    "consumptions": [],
                }
            )
            return render(request, self.template_name, context)

        daily_record, _ = DailyRecord.objects.get_or_create(
            user=request.user, date=timezone.localdate()
        )
        form = FoodConsumptionForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.daily_record = daily_record
            instance.save()
            return redirect("core:add_food")

        context = _build_today_context(request.user)
        context.update(
            {
                "active_nav": "add_food",
                "form": form,
                "foods": Food.objects.filter(is_active=True)[:20],
                "consumptions": FoodConsumption.objects.filter(
                    daily_record=daily_record
                ).select_related("food"),
            }
        )
        return render(request, self.template_name, context)


class ActivityView(View):
    template_name = "core/activity.html"

    def get(self, request):
        context = _build_today_context(request.user)
        context.update(
            {
                "active_nav": "activity",
                "form": ActivityRecordForm(),
                "activities": PhysicalActivity.objects.filter(is_active=True)[:20],
                "records": (
                    ActivityRecord.objects.filter(daily_record=context["daily_record"]).select_related("activity")
                    if request.user.is_authenticated
                    else []
                ),
            }
        )
        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.is_authenticated:
            context = _build_today_context(request.user)
            context.update(
                {
                    "active_nav": "activity",
                    "form": ActivityRecordForm(request.POST),
                    "form_error": "Necesitas iniciar sesion para registrar actividad.",
                    "activities": PhysicalActivity.objects.filter(is_active=True)[:20],
                    "records": [],
                }
            )
            return render(request, self.template_name, context)

        daily_record, _ = DailyRecord.objects.get_or_create(
            user=request.user, date=timezone.localdate()
        )
        form = ActivityRecordForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.daily_record = daily_record
            instance.save()
            return redirect("core:activity")

        context = _build_today_context(request.user)
        context.update(
            {
                "active_nav": "activity",
                "form": form,
                "activities": PhysicalActivity.objects.filter(is_active=True)[:20],
                "records": ActivityRecord.objects.filter(
                    daily_record=daily_record
                ).select_related("activity"),
            }
        )
        return render(request, self.template_name, context)


class HistoryView(TemplateView):
    template_name = "core/history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(_build_today_context(self.request.user))
        context.update({"active_nav": "history"})

        if not self.request.user.is_authenticated:
            context["history_rows"] = []
            return context

        history_rows = []
        records = (
            DailyRecord.objects.filter(user=self.request.user)
            .order_by("-date")
            .prefetch_related("food_consumptions__food", "activity_records__activity")[:14]
        )
        for record in records:
            calories = Decimal("0")
            for item in record.food_consumptions.all():
                factor = item.amount_g / Decimal("100")
                calories += factor * item.food.calories_per_100g

            burned = sum(
                item.calories_burned_estimated or 0
                for item in record.activity_records.all()
            )
            history_rows.append(
                {
                    "date": record.date,
                    "calories": calories,
                    "burned": burned,
                    "score": getattr(record.evaluation, "score", 0),
                }
            )

        context["history_rows"] = history_rows
        return context


class ProfileView(View):
    template_name = "core/profile.html"

    def get(self, request):
        context = _build_today_context(request.user)
        context.update({"active_nav": "profile"})

        if not request.user.is_authenticated:
            context.update({"requires_auth": True, "form": None})
            return render(request, self.template_name, context)

        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(instance=profile)
        context.update({"requires_auth": False, "form": form})
        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.is_authenticated:
            return self.get(request)

        profile, _ = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("core:profile")

        context = _build_today_context(request.user)
        context.update({"active_nav": "profile", "requires_auth": False, "form": form})
        return render(request, self.template_name, context)


class HelpView(TemplateView):
    template_name = "core/help.html"
