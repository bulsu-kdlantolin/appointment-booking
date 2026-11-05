from django.contrib import admin
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.db import models
from django.template.response import TemplateResponse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    BooleanRadioFilter as UnfoldBooleanRadioFilter,
    ChoicesRadioFilter,
    RelatedDropdownFilter,
)
from unfold.contrib.filters.forms import RadioForm
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.widgets import UnfoldAdminSplitDateTimeWidget

from .models import Appointment, Client, Service


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


@admin.register(Appointment)
class AppointmentAdmin(ModelAdmin):
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
        ("scheduled_at", admin.DateFieldListFilter),
        ("service", RelatedRadioFilter),
        ("status", ChoicesRadioFilter),
        ("is_archived", BooleanRadioFilter),
    )
    search_fields = ("client__full_name", "client__email", "service__name")
    ordering = ("scheduled_at",)

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
