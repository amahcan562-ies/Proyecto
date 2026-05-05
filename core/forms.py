from django import forms

from activity.models import ActivityRecord, PhysicalActivity
from nutrition.models import Food, FoodConsumption
from users.models import Profile


class FoodConsumptionForm(forms.ModelForm):
    class Meta:
        model = FoodConsumption
        fields = ["food", "amount_g", "meal_type", "consumed_at", "notes"]
        widgets = {
            "consumed_at": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["food"].queryset = Food.objects.filter(is_active=True)


class ActivityRecordForm(forms.ModelForm):
    class Meta:
        model = ActivityRecord
        fields = ["activity", "duration_min", "performed_at", "notes"]
        widgets = {
            "performed_at": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["activity"].queryset = PhysicalActivity.objects.filter(is_active=True)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "birth_date",
            "sex",
            "height_cm",
            "weight_kg",
            "target_weight_kg",
            "goal",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

