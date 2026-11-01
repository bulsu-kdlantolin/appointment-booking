from django.shortcuts import get_object_or_404, render

from .models import Appointment


def home(request):
    """List all appointments (HttpRequest in, HttpResponse out)."""
    appointments = Appointment.objects.all()
    return render(request, 'appointments/home.html',
                  {'appointments': appointments})


def detail(request, pk):
    """Show one appointment, or return a 404 if it does not exist."""
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/detail.html',
                  {'appointment': appointment})
