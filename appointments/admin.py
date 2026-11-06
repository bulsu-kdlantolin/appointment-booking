from datetime import timedelta
from django import forms
from django.contrib import admin
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.db import models
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    BooleanRadioFilter as UnfoldBooleanRadioFilter,
    ChoicesRadioFilter,
    RadioFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.filters.forms import RadioForm
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.widgets import UnfoldAdminSplitDateTimeWidget

from .models import Appointment, Client, Service


# Logs out the administrator and renders the custom styled logout screen.
def custom_admin_logout(request, extra_context=None):
    auth_logout(request)
    context = {
        **admin.site.each_context(request),
        "title": "Logged out",
        "has_permission": False,
        **(extra_context or {}),
    }
    return TemplateResponse(request, "registration/logged_out.html", context)


admin.site.logout = custom_admin_logout


class BooleanRadioFilter(UnfoldBooleanRadioFilter):
    form_class = RadioForm


class RelatedRadioFilter(RelatedDropdownFilter):
    form_class = RadioForm

    def choices(self, changelist):
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None

        if add_facets and facet_counts:
            choices = [self.all_option]
            for pk_val, val in self.lookup_choices:
                count = facet_counts.get(f"{pk_val}__c", "-")
                choice = (pk_val, f"{val} ({count})")
                choices.append(choice)
        else:
            choices = [self.all_option, *self.lookup_choices]

        yield {
            "form": self.form_class(
                label=self.title,
                name=self.lookup_kwarg,
                choices=choices,
                data={self.lookup_kwarg: self.value()},
            ),
        }


# Custom admin filter providing radio button choices for appointment date ranges.
class ScheduledAtRadioFilter(RadioFilter):
    title = _("Scheduled at")
    parameter_name = "scheduled_at"
    all_option = ["", _("Any date")]

    def lookups(self, request, model_admin):
        return [
            ("today", _("Today")),
            ("week", _("This week")),
            ("month", _("This month")),
            ("year", _("This year")),
        ]

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset

        now = timezone.now()
        if timezone.is_aware(now):
            now = timezone.localtime(now)
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if val == "today":
            tomorrow = today + timedelta(days=1)
            return queryset.filter(scheduled_at__gte=today, scheduled_at__lt=tomorrow)
        elif val == "week":
            start_of_week = today - timedelta(days=today.weekday())
            next_week = start_of_week + timedelta(days=7)
            return queryset.filter(scheduled_at__gte=start_of_week, scheduled_at__lt=next_week)
        elif val == "month":
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
            return queryset.filter(
                scheduled_at__gte=today.replace(day=1),
                scheduled_at__lt=next_month,
            )
        elif val == "year":
            next_year = today.replace(year=today.year + 1, month=1, day=1)
            return queryset.filter(
                scheduled_at__gte=today.replace(month=1, day=1),
                scheduled_at__lt=next_year,
            )
        return queryset


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    compressed_fields = True
    warn_unsaved_form = True
    list_filter = (
        ("is_staff", BooleanRadioFilter),
        ("is_superuser", BooleanRadioFilter),
        ("is_active", BooleanRadioFilter),
        ("groups", RelatedRadioFilter),
    )


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("full_name", "email", "phone")
    search_fields = ("full_name", "email", "phone")
    ordering = ("full_name",)


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    list_display = ("name", "duration_minutes", "active")
    list_filter = (
        ("active", BooleanRadioFilter),
    )
    search_fields = ("name",)
    ordering = ("name",)


# Form used in the admin panel with past-date and scheduling validation.
class AppointmentAdminForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = "__all__"

    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data.get("scheduled_at")
        status = self.cleaned_data.get("status")
        is_archived = self.cleaned_data.get("is_archived")

        if scheduled_at:
            # Enforce 30-minute interval slots (:00 or :30) in admin
            if scheduled_at.minute not in (0, 30):
                raise forms.ValidationError(
                    "Appointments must start on a 30-minute slot (e.g., 9:00 or 9:30)."
                )

            if status == "scheduled" and not is_archived:
                # Check if creating a new appointment or changing the date on an existing one
                if not self.instance.pk or self.instance.scheduled_at != scheduled_at:
                    if scheduled_at < timezone.now():
                        raise forms.ValidationError("Appointments cannot be scheduled in the past.")

        return scheduled_at


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
    form = AppointmentAdminForm
    compressed_fields = True
    warn_unsaved_form = True
    formfield_overrides = {
        models.DateTimeField: {
            "widget": UnfoldAdminSplitDateTimeWidget,
        },
    }
    list_display = (
        "client",
        "service",
        "scheduled_at",
        "status_badge",
        "is_archived",
    )
    list_filter = (
        ScheduledAtRadioFilter,
        ("service", RelatedRadioFilter),
        ("status", ChoicesRadioFilter),
        ("is_archived", BooleanRadioFilter),
    )
    search_fields = ("client__full_name", "client__email", "service__name")
    ordering = ("scheduled_at",)

    # Renders a color-coded HTML badge displaying the appointment status.
    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {
            "scheduled": ("#eff6ff", "#1d4ed8", "#bfdbfe"),
            "completed": ("#ecfdf5", "#047857", "#a7f3d0"),
            "cancelled": ("#fef2f2", "#b91c1c", "#fecaca"),
        }
        bg, text, border = colors.get(obj.status, ("#f1f5f9", "#475569", "#cbd5e1"))
        return format_html(
            '<span style="display:inline-flex; align-items:center; background:{}; color:{}; border:1px solid {}; padding:0.25rem 0.65rem; border-radius:9999px; font-weight:600; font-size:0.75rem; line-height:1;">{}</span>',
            bg,
            text,
            border,
            obj.get_status_display(),
        )
