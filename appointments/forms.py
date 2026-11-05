from django import forms
from django.utils import timezone
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["client", "service", "scheduled_at", "status", "notes"]
        widgets = {
            "scheduled_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "sr-only"},
                format="%Y-%m-%dT%H:%M",
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "block w-full rounded-xl border border-slate-300 bg-white px-3.5 py-3 text-sm text-slate-900 placeholder:text-slate-400 transition hover:border-blue-400 focus:border-blue-600 focus:outline-none focus:ring-4 focus:ring-blue-100 font-sans resize-y leading-relaxed",
                    "rows": 4,
                    "placeholder": "Add any notes or special requirements here...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # datetime-local submits "2026-11-07T14:30" — tell Django to parse that format
        self.fields["scheduled_at"].input_formats = [
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
        ]

    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data["scheduled_at"]

        if scheduled_at < timezone.now():
            raise forms.ValidationError("The appointment cannot be in the past.")

        if scheduled_at.minute not in (0, 30):
            raise forms.ValidationError(
                "Appointments must start on a 30-minute slot (e.g., 9:00 or 9:30)."
            )

        return scheduled_at

    def clean(self):
        cleaned = super().clean()
        scheduled_at = cleaned.get("scheduled_at")
        if not scheduled_at or cleaned.get("status") != "scheduled":
            return cleaned

        conflicts = Appointment.objects.filter(
            scheduled_at=scheduled_at,
            status="scheduled",
            is_archived=False,
        )

        # When editing, don't count the record as conflicting with itself
        if self.instance.pk:
            conflicts = conflicts.exclude(pk=self.instance.pk)

        if conflicts.exists():
            raise forms.ValidationError(
                "Another scheduled appointment already occupies this time slot."
            )

        return cleaned
