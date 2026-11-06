from django.urls import path
from . import views

app_name = "appointments"

# URL patterns mapping browser endpoints to their corresponding appointment view functions.
urlpatterns = [
    path("", views.appointment_list, name="list"),
    path("", views.appointment_list, name="appointment_list"),
    path("appointments/new/", views.appointment_create, name="create"),
    path("appointments/new/", views.appointment_create, name="appointment_create"),
    path("appointments/<int:pk>/", views.appointment_detail, name="detail"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("appointments/<int:pk>/edit/", views.appointment_update, name="update"),
    path("appointments/<int:pk>/edit/", views.appointment_update, name="appointment_update"),
    path("appointments/<int:pk>/archive/", views.appointment_archive, name="archive"),
    path("appointments/<int:pk>/archive/", views.appointment_archive, name="appointment_archive"),
    path("appointments/<int:pk>/unarchive/", views.appointment_unarchive, name="unarchive"),
    path("appointments/<int:pk>/unarchive/", views.appointment_unarchive, name="appointment_unarchive"),
    path("appointments/<int:pk>/delete/", views.appointment_delete, name="delete"),
    path("appointments/<int:pk>/delete/", views.appointment_delete, name="appointment_delete"),
]
