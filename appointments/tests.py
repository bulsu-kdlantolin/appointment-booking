from datetime import timedelta
from django.contrib import admin as django_admin
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.urls import reverse
from django.utils import timezone
from appointments.admin import AppointmentAdmin
from .models import Client, Service, Appointment
from .forms import AppointmentForm


class AppointmentFormTests(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(
            full_name="Test Client", email="t@t.com", phone="0917"
        )
        self.service = Service.objects.create(name="Cut", duration_minutes=30)

    def _future_slot(self, days=1):
        return (timezone.now() + timedelta(days=days)).replace(
            minute=0, second=0, microsecond=0
        )

    def test_past_date_rejected(self):
        past = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        form = AppointmentForm(data={
            "client": self.client_obj.pk,
            "service": self.service.pk,
            "scheduled_at": past,
            "status": "scheduled",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("scheduled_at", form.errors)

    def test_off_grid_minute_rejected(self):
        slot = self._future_slot().replace(minute=15)
        form = AppointmentForm(data={
            "client": self.client_obj.pk,
            "service": self.service.pk,
            "scheduled_at": slot.strftime("%Y-%m-%dT%H:%M"),
            "status": "scheduled",
        })
        self.assertFalse(form.is_valid())

    def test_conflict_rejected(self):
        slot = self._future_slot()
        Appointment.objects.create(
            client=self.client_obj, service=self.service, scheduled_at=slot
        )
        form = AppointmentForm(data={
            "client": self.client_obj.pk,
            "service": self.service.pk,
            "scheduled_at": slot.strftime("%Y-%m-%dT%H:%M"),
            "status": "scheduled",
        })
        self.assertFalse(form.is_valid())

    def test_edit_does_not_conflict_with_self(self):
        slot = self._future_slot()
        appt = Appointment.objects.create(
            client=self.client_obj, service=self.service, scheduled_at=slot
        )
        form = AppointmentForm(
            data={
                "client": self.client_obj.pk,
                "service": self.service.pk,
                "scheduled_at": slot.strftime("%Y-%m-%dT%H:%M"),
                "status": "scheduled",
            },
            instance=appt,
        )
        self.assertTrue(form.is_valid())

    def test_archived_row_does_not_block(self):
        slot = self._future_slot()
        Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=slot,
            is_archived=True,
            archived_at=timezone.now(),
        )
        form = AppointmentForm(data={
            "client": self.client_obj.pk,
            "service": self.service.pk,
            "scheduled_at": slot.strftime("%Y-%m-%dT%H:%M"),
            "status": "scheduled",
        })
        self.assertTrue(form.is_valid())

    def test_completed_appointment_does_not_block_slot(self):
        slot = self._future_slot()
        Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=slot,
            status="completed",
        )
        form = AppointmentForm(data={
            "client": self.client_obj.pk,
            "service": self.service.pk,
            "scheduled_at": slot.strftime("%Y-%m-%dT%H:%M"),
            "status": "scheduled",
        })
        self.assertTrue(form.is_valid())

    def test_admin_cannot_unarchive_into_a_conflicting_slot(self):
        slot = self._future_slot()
        Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=slot,
        )
        archived = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=slot,
            is_archived=True,
            archived_at=timezone.now(),
        )

        request = RequestFactory().get("/admin/")
        request.user = AnonymousUser()
        admin_form_class = AppointmentAdmin(
            Appointment, django_admin.site
        ).get_form(request, obj=archived)
        form = admin_form_class(
            data={
                "client": self.client_obj.pk,
                "service": self.service.pk,
                "scheduled_at": slot.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "scheduled",
                "notes": "",
                "is_archived": "",
                "archived_at": archived.archived_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            instance=archived,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("scheduled_at", form.errors)


class AppointmentWorkflowTests(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(
            full_name="Workflow Client", email="workflow@example.com", phone="0918"
        )
        self.service = Service.objects.create(name="Consultation", duration_minutes=45)

    def _slot(self, days=1):
        return (timezone.now() + timedelta(days=days)).replace(
            minute=0, second=0, microsecond=0
        )

    def _data(self, slot, status="scheduled", notes=""):
        return {
            "client": self.client_obj.pk,
            "service": self.service.pk,
            "scheduled_at": slot.strftime("%Y-%m-%dT%H:%M"),
            "status": status,
            "notes": notes,
        }

    def test_create_saves_and_redirects_to_detail(self):
        response = self.client.post(
            reverse("appointments:create"),
            self._data(self._slot(), notes="Bring documents"),
        )
        appointment = Appointment.objects.get()
        self.assertRedirects(
            response, reverse("appointments:detail", args=[appointment.pk])
        )
        self.assertEqual(appointment.notes, "Bring documents")

    def test_invalid_create_renders_errors_without_saving(self):
        response = self.client.post(
            reverse("appointments:create"),
            self._data(self._slot(), status="invalid"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")
        self.assertEqual(Appointment.objects.count(), 0)

    def test_list_shows_upcoming_and_hides_past(self):
        upcoming = Appointment.objects.create(
            client=self.client_obj, service=self.service, scheduled_at=self._slot()
        )
        Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=self._slot(days=-1),
        )
        response = self.client.get(reverse("appointments:list"))
        self.assertContains(response, "Workflow Client")
        self.assertEqual(response.context["appointments"].count(), 1)

    def test_detail_unknown_returns_404_and_archived_is_viewable(self):
        response = self.client.get(reverse("appointments:detail", args=[9999]))
        self.assertEqual(response.status_code, 404)
        archived = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=self._slot(),
            is_archived=True,
            archived_at=timezone.now(),
        )
        response = self.client.get(
            reverse("appointments:detail", args=[archived.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Archived")

    def test_update_saves_changed_values(self):
        appointment = Appointment.objects.create(
            client=self.client_obj, service=self.service, scheduled_at=self._slot()
        )
        response = self.client.post(
            reverse("appointments:update", args=[appointment.pk]),
            self._data(self._slot(days=2), status="completed", notes="Done"),
        )
        self.assertRedirects(
            response, reverse("appointments:detail", args=[appointment.pk])
        )
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, "completed")
        self.assertEqual(appointment.notes, "Done")

    def test_archive_confirmation_preserves_the_record(self):
        appointment = Appointment.objects.create(
            client=self.client_obj, service=self.service, scheduled_at=self._slot()
        )
        get_response = self.client.get(
            reverse("appointments:archive", args=[appointment.pk])
        )
        self.assertEqual(get_response.status_code, 200)
        response = self.client.post(
            reverse("appointments:archive", args=[appointment.pk])
        )
        self.assertRedirects(response, reverse("appointments:list"))
        appointment.refresh_from_db()
        self.assertTrue(appointment.is_archived)
        self.assertIsNotNone(appointment.archived_at)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_delete_confirmation_archives_the_record(self):
        appointment = Appointment.objects.create(
            client=self.client_obj, service=self.service, scheduled_at=self._slot()
        )
        get_response = self.client.get(
            reverse("appointments:delete", args=[appointment.pk])
        )
        self.assertEqual(get_response.status_code, 200)
        response = self.client.post(
            reverse("appointments:delete", args=[appointment.pk])
        )
        self.assertRedirects(response, reverse("appointments:list"))
        appointment.refresh_from_db()
        self.assertTrue(appointment.is_archived)
        self.assertIsNotNone(appointment.archived_at)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_delete_overlay_permanently_deletes_the_record(self):
        appointment = Appointment.objects.create(
            client=self.client_obj, service=self.service, scheduled_at=self._slot()
        )
        response = self.client.post(
            reverse("appointments:delete", args=[appointment.pk]),
            data={"action": "delete"},
        )
        self.assertRedirects(response, reverse("appointments:list"))
        self.assertFalse(Appointment.objects.filter(pk=appointment.pk).exists())

    def test_unarchive_restores_an_archived_appointment(self):
        appointment = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=self._slot(),
            is_archived=True,
            archived_at=timezone.now(),
        )
        response = self.client.post(
            reverse("appointments:unarchive", args=[appointment.pk])
        )
        self.assertRedirects(
            response, reverse("appointments:detail", args=[appointment.pk])
        )
        appointment.refresh_from_db()
        self.assertFalse(appointment.is_archived)
        self.assertIsNone(appointment.archived_at)

    def test_unarchive_conflict_keeps_appointment_archived(self):
        slot = self._slot()
        Appointment.objects.create(
            client=self.client_obj, service=self.service, scheduled_at=slot
        )
        archived = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=slot,
            is_archived=True,
            archived_at=timezone.now(),
        )
        response = self.client.post(
            reverse("appointments:unarchive", args=[archived.pk])
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("cannot be unarchived", response.content.decode())
        archived.refresh_from_db()
        self.assertTrue(archived.is_archived)
        self.assertIsNotNone(archived.archived_at)

    def test_search_and_status_filter(self):
        matching = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=self._slot(),
            status="completed",
        )
        other_client = Client.objects.create(
            full_name="Other Client", email="other@example.com", phone="0919"
        )
        Appointment.objects.create(
            client=other_client,
            service=self.service,
            scheduled_at=self._slot(days=2),
        )
        response = self.client.get(
            reverse("appointments:list"),
            {"q": "Workflow", "status": "completed"},
        )
        self.assertContains(response, "Workflow Client")
        self.assertEqual(response.context["appointments"].count(), 1)

    def test_list_uses_ampm_time_format_and_live_filters(self):
        Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=self._slot().replace(hour=14),
        )
        response = self.client.get(reverse("appointments:list"))
        self.assertContains(response, "2:00 PM")
        self.assertContains(response, 'id="appointment-filters"')
        self.assertContains(response, 'searchField.addEventListener("input"')
        self.assertContains(response, 'statusToggle.addEventListener("click"')
        self.assertContains(response, 'appointmentFilters.submit()')

    def test_form_uses_themed_date_time_picker(self):
        response = self.client.get(reverse("appointments:create"))
        self.assertContains(response, "cdn.jsdelivr.net/npm/flatpickr")
        self.assertContains(response, 'id="scheduled-date"')
        self.assertContains(response, 'id="scheduled-time"')
        self.assertContains(response, "minuteIncrement: 30")
        self.assertContains(response, 'monthSelectorType: "static"')
        self.assertContains(response, "flatpickr-time input::-webkit-inner-spin-button")


class AppointmentModelAndQueryTests(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(
            full_name="Alice Smith", email="alice@example.com", phone="09123456789"
        )
        self.service = Service.objects.create(name="Hair Styling", duration_minutes=60)
        self.now = timezone.now().replace(minute=0, second=0, microsecond=0)
        self.appointment = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=self.now + timedelta(days=1),
        )

    def test_str_methods(self):
        self.assertEqual(str(self.service), "Hair Styling")
        self.assertEqual(str(self.client_obj), "Alice Smith")
        expected_appt_str = f"Alice Smith — Hair Styling @ {self.appointment.scheduled_at:%Y-%m-%d %H:%M}"
        self.assertEqual(str(self.appointment), expected_appt_str)

    def test_meta_ordering_scheduled_at(self):
        self.assertEqual(Appointment._meta.ordering, ["scheduled_at"])

    def test_list_query_uses_select_related(self):
        response = self.client.get(reverse("appointments:list"))
        appointments_qs = response.context["appointments"]
        self.assertEqual(
            appointments_qs.query.select_related,
            {"client": {}, "service": {}},
        )

    def test_default_list_filters_out_archived_records(self):
        archived = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=self.now + timedelta(days=2),
            is_archived=True,
            archived_at=timezone.now(),
        )
        response = self.client.get(reverse("appointments:list"))
        appointments = response.context["appointments"]
        self.assertIn(self.appointment, appointments)
        self.assertNotIn(archived, appointments)

    def test_delete_confirmation_post_sets_archived_instead_of_delete(self):
        appt = Appointment.objects.create(
            client=self.client_obj,
            service=self.service,
            scheduled_at=self.now + timedelta(days=3),
        )
        response = self.client.post(reverse("appointments:delete", args=[appt.pk]))
        self.assertRedirects(response, reverse("appointments:list"))
        appt.refresh_from_db()
        self.assertTrue(appt.is_archived)
        self.assertIsNotNone(appt.archived_at)
        self.assertTrue(Appointment.objects.filter(pk=appt.pk).exists())


class UserGroupPermissionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="staff_member", password="password123", is_staff=True, is_superuser=False
        )
        self.superuser = User.objects.create_superuser(
            username="super_admin", password="password123", email="admin@example.com"
        )
        self.perm_view_appt = Permission.objects.get(
            codename="view_appointment", content_type__app_label="appointments"
        )
        self.perm_add_appt = Permission.objects.get(
            codename="add_appointment", content_type__app_label="appointments"
        )

    def test_superuser_has_all_permissions(self):
        self.assertTrue(self.superuser.has_perm("appointments.view_appointment"))
        self.assertTrue(self.superuser.has_perm("appointments.add_appointment"))
        self.assertTrue(self.superuser.has_perm("appointments.delete_appointment"))
        self.assertTrue(self.superuser.has_perm("appointments.view_client"))

    def test_staff_without_permissions_is_denied(self):
        self.assertFalse(self.user.has_perm("appointments.view_appointment"))
        self.client.login(username="staff_member", password="password123")
        response = self.client.get("/admin/appointments/appointment/")
        self.assertEqual(response.status_code, 403)

    def test_group_permissions_are_inherited_and_enforced(self):
        group = Group.objects.create(name="Appointment Viewers")
        group.permissions.add(self.perm_view_appt)
        self.user.groups.add(group)

        # Refresh user from DB to reload cached permissions
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.has_perm("appointments.view_appointment"))
        self.assertFalse(user.has_perm("appointments.add_appointment"))
        self.assertFalse(user.has_perm("appointments.view_client"))

        # Verify Django Admin respects group permissions
        self.client.login(username="staff_member", password="password123")
        view_response = self.client.get("/admin/appointments/appointment/")
        self.assertEqual(view_response.status_code, 200)

        # Denied models / actions outside group permissions
        forbidden_client = self.client.get("/admin/appointments/client/")
        self.assertEqual(forbidden_client.status_code, 403)
        forbidden_add = self.client.get("/admin/appointments/appointment/add/")
        self.assertEqual(forbidden_add.status_code, 403)

    def test_direct_user_permission_is_applied(self):
        self.user.user_permissions.add(self.perm_view_appt, self.perm_add_appt)
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.has_perm("appointments.view_appointment"))
        self.assertTrue(user.has_perm("appointments.add_appointment"))

        self.client.login(username="staff_member", password="password123")
        add_response = self.client.get("/admin/appointments/appointment/add/")
        self.assertEqual(add_response.status_code, 200)

