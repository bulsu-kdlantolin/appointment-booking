from django.db import models


class Appointment(models.Model):
    """One booked appointment. Data rules live in the model."""

    class Service(models.TextChoices):
        CHECKUP = 'checkup', 'General Check-up'
        CONSULT = 'consult', 'Consultation'
        FOLLOWUP = 'followup', 'Follow-up Visit'

    client_name = models.CharField(max_length=100)
    email = models.EmailField()
    service = models.CharField(max_length=20, choices=Service.choices)
    scheduled_for = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_for']

    def __str__(self):
        return f'{self.client_name} - {self.get_service_display()}'
