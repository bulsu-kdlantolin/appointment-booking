from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Appointment, Service
from .forms import AppointmentForm


def appointment_list(request):
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    service_id = request.GET.get("service", "").strip()
    date_filter = request.GET.get("date", "").strip()
    show_archived = request.GET.get("archived") == "1"

    if show_archived:
        appointments = Appointment.objects.filter(
            is_archived=True
        ).select_related("client", "service")
    else:
        appointments = Appointment.objects.filter(
            is_archived=False,
            scheduled_at__gte=timezone.now(),
        ).select_related("client", "service")

    if q:
        appointments = appointments.filter(client__full_name__icontains=q)
    if status:
        appointments = appointments.filter(status=status)
    if service_id:
        appointments = appointments.filter(service_id=service_id)
    if date_filter:
        today = timezone.localdate()
        if date_filter == "today":
            appointments = appointments.filter(scheduled_at__date=today)
        elif date_filter == "tomorrow":
            appointments = appointments.filter(scheduled_at__date=today + timedelta(days=1))
        elif date_filter == "week":
            appointments = appointments.filter(
                scheduled_at__date__gte=today,
                scheduled_at__date__lte=today + timedelta(days=7),
            )
        elif date_filter == "month":
            appointments = appointments.filter(
                scheduled_at__year=today.year,
                scheduled_at__month=today.month,
            )
        else:
            try:
                parsed_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                appointments = appointments.filter(scheduled_at__date=parsed_date)
            except ValueError:
                pass

    services = Service.objects.all().order_by("name")

    return render(
        request,
        "appointments/appointment_list.html",
        {
            "appointments": appointments,
            "services": services,
            "q": q,
            "status": status,
            "service_id": service_id,
            "date_filter": date_filter,
            "show_archived": show_archived,
        },
    )


def appointment_detail(request, pk):
    appointment = get_object_or_404(
        Appointment.objects.select_related("client", "service"),
        pk=pk,
    )
    return render(
        request,
        "appointments/appointment_detail.html",
        {"appointment": appointment},
    )


def appointment_unarchive(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        appointment.is_archived = False
        appointment.archived_at = None
        try:
            appointment.full_clean()
        except ValidationError as error:
            appointment = Appointment.objects.select_related(
                "client", "service"
            ).get(pk=pk)
            return render(
                request,
                "appointments/appointment_detail.html",
                {
                    "appointment": appointment,
                    "unarchive_error": error.message_dict.get(
                        "scheduled_at", error.messages
                    ),
                },
                status=400,
            )

        appointment.save(update_fields=["is_archived", "archived_at", "updated_at"])
        return redirect("appointments:detail", pk=appointment.pk)

    return redirect("appointments:detail", pk=appointment.pk)


def appointment_create(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            return redirect("appointments:detail", pk=appointment.pk)
    else:
        form = AppointmentForm()

    return render(
        request,
        "appointments/appointment_form.html",
        {"form": form},
    )


def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect("appointments:detail", pk=appointment.pk)
    else:
        form = AppointmentForm(instance=appointment)

    return render(
        request,
        "appointments/appointment_form.html",
        {"form": form},
    )


def appointment_archive(request, pk):
    return appointment_delete(request, pk)


def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        # Complete delete (from delete overlay) vs soft delete (archive)
        if request.POST.get("action") == "delete" or request.POST.get("permanent") == "1":
            appointment.delete()
            return redirect("appointments:list")

        # Soft delete (archive) as per requirement:
        # /appointments/<int:pk>/delete/ appointment_delete Confirmation on GET; archive (soft delete) on POST
        appointment.is_archived = True
        appointment.archived_at = timezone.now()
        appointment.save()
        return redirect("appointments:list")

    return render(
        request,
        "appointments/appointment_confirm_delete.html",
        {"appointment": appointment},
    )

def custom_404(request, exception=None):
    return render(request, "404.html", status=404)
