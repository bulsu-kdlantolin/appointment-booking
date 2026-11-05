from django.core.exceptions import ValidationError
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    duration_minutes = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)

    def __str__(self):
        return self.full_name


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    notes = models.TextField(blank=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_at"]

    def clean(self):
        super().clean()
        if (
            self.status != "scheduled"
            or self.is_archived
            or not self.scheduled_at
        ):
            return

        conflicts = Appointment.objects.filter(
            scheduled_at=self.scheduled_at,
            status="scheduled",
            is_archived=False,
        ).exclude(pk=self.pk)

        if conflicts.exists():
            raise ValidationError(
                {"scheduled_at": "Another scheduled appointment already occupies this time slot."}
            )

    def __str__(self):
        return f"{self.client.full_name} — {self.service.name} @ {self.scheduled_at:%Y-%m-%d %H:%M}"