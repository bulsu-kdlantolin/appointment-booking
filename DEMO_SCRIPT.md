# 🎬 Appointment Booking System — Live Demonstration Script

**Course:** 4th Year BSIT — Python Web Development  
**Project:** Appointment Booking System  
**Framework:** Django 6.1+, SQLite, Django Unfold  
**Duration:** ~5–7 Minutes  

---

## 📋 Quick Pre-Demo Checklist

- [ ] Virtual environment activated: `.\.venv\Scripts\Activate.ps1`
- [ ] Dev server running: `python manage.py runserver` (Terminal 1)
- [ ] Browser tabs open:
  - Tab 1: Public Site — [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
  - Tab 2: Admin Panel — [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (Credentials: `kiand` / `admin1234`)
  - Tab 3: Code editor (VS Code / Antigravity) with project open
- [ ] Clean terminal ready for running tests (`python manage.py test`)

---

## ⏱️ Demo Agenda & Timeline

| Section | Topic | Duration |
| :--- | :--- | :--- |
| **Part 1** | Introduction & System Architecture | ~1 min |
| **Part 2** | Public Interface (List, Search, Filter) | ~1.5 min |
| **Part 3** | Appointment Booking & Form Validations | ~1.5 min |
| **Part 4** | Django Unfold Admin Dashboard Walkthrough | ~1.5 min |
| **Part 5** | Automated Tests & Conclusion | ~0.5 min |

---

## 🎙️ Step-by-Step Script

### Part 1: Introduction & Architecture (~1 min)

> **🗣️ What to Say:**  
> "Good day, instructor and classmates. Today I am presenting our **Appointment Booking System**, built using **Django** and styled with **Django Unfold** and Tailwind CSS.  
> The system is designed for service-oriented businesses to easily schedule, track, manage, and archive client appointments. It features a modern client-facing public interface and a fully customized, role-based administrative dashboard."

> **🖥️ What to Show:**  
> - Show the clean project structure in VS Code (`appointments/`, `config/`, `static/`).
> - Briefly mention the 3 core models: **Client**, **Service**, and **Appointment**.

---

### Part 2: Public Interface — List, Search & Filter (~1.5 min)

> **🖥️ What to Do:**  
> 1. Switch to Tab 1: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
> 2. Point out the responsive layout, appointment cards/table, and readable status badges (`Scheduled`, `Completed`, `Cancelled`).
> 3. Click the **Status Filter** dropdown and choose **"Scheduled"**.
> 4. Click the **Date Filter** dropdown and choose **"This Year"** or **"This Month"**.
> 5. Type a client name (e.g., `"Maria"`) in the search bar and press Enter.
> 6. Clear search to restore the full list.

> **🗣️ What to Say:**  
> "On our public landing page, visitors and staff can immediately view upcoming appointments.  
> Notice our search and filtering system: we can filter appointments by status, such as Scheduled or Completed, or by date range—including Today, This Week, This Month, and This Year.  
> Users can also use the real-time search bar to look up appointments by client name or service."

---

### Part 3: Booking Workflow & Input Validation (~1.5 min)

> **🖥️ What to Do:**  
> 1. Click the **"+ Book Appointment"** button to open `/appointments/new/`.
> 2. **Demonstrate Past-Date Validation:**
>    - Select a Client and Service.
>    - Pick a date in the past (e.g., yesterday).
>    - Click **"Confirm Booking"**.
>    - Point out the error message: *"Appointments cannot be scheduled in the past."*
> 3. **Demonstrate Conflict / Double-Booking Validation:**
>    - Select an existing appointment's exact date & time slot.
>    - Submit and show the conflict warning message.
> 4. **Demonstrate Successful Booking:**
>    - Select a valid future date/time using the integrated Flatpickr picker.
>    - Click **"Confirm Booking"**.
>    - Show the green success message and the newly created appointment in the list.
> 5. Click the new appointment to view its **Detail Page**, then demonstrate the **Edit** and **Archive** buttons.

> **🗣️ What to Say:**  
> "Now let's book an appointment to demonstrate our `AppointmentForm` validation.  
> First, if someone attempts to book a date in the past, our custom validation catches it immediately and informs the user.  
> Second, our system prevents double-booking conflicts for overlapping time slots.  
> When we enter valid details, the appointment is created instantly, redirected to the overview page with a confirmation toast, and can be viewed, updated, or safely archived."

---

### Part 4: Modern Admin Dashboard (Django Unfold) (~1.5 min)

> **🖥️ What to Do:**  
> 1. Switch to Tab 2: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).
> 2. Highlight the modern **Django Unfold** interface (Tailwind CSS, dark mode support).
> 3. Click the **Dark Mode** toggle in the top-right to demonstrate seamless theme switching.
> 4. Navigate to **Appointments**:
>    - Show the **Custom Radio Filters** on the right: *Status* and *Scheduled at* (Today, This week, This month, This year).
>    - Click the table header column arrows to demonstrate **sorting** (Ascending / Descending order).
> 5. Click an appointment to open the edit form:
>    - Demonstrate the **3-Dots Related Widget Menu**: click the 3-dots next to *Client* or *Service* to show the popup modal for viewing/adding records without navigating away.
> 6. Navigate to **Users & Groups** to show administrative permissions.

> **🗣️ What to Say:**  
> "Behind the scenes, we upgraded Django's default admin into a modern, production-grade dashboard using Django Unfold.  
> It supports both full Light and Dark modes.  
> We customized the changelist with radio button filters for date ranges and appointment statuses, fully interactive sort headers, and inline 3-dots relation widgets that let admins view, add, or edit clients and services directly inside modal popups."

---

### Part 5: Automated Testing & Wrap-Up (~0.5 min)

> **🖥️ What to Do:**  
> 1. Switch to the terminal.
> 2. Run: `python manage.py test`
> 3. Point out the output: `Ran 33 tests ... OK`.

> **🗣️ What to Say:**  
> "To guarantee stability, we wrote a comprehensive automated test suite covering model constraints, form validation, conflict checking, query optimizations, and view permissions. All 33 tests pass with 0 errors.  
> This concludes our live demonstration. Thank you, and I am ready for any questions!"

---

## ❓ Anticipated Q&A (Be Prepared!)

| Question | Answer |
| :--- | :--- |
| **How do you prevent scheduling conflicts?** | In `AppointmentForm.clean()`, we query `Appointment.objects.filter(scheduled_at=scheduled_at)` excluding the current instance, raising a `ValidationError` if an overlap exists. |
| **Why use Django Unfold instead of standard admin?** | Unfold provides a responsive Tailwind CSS UI, Alpine.js interactivity, customizable sidebars, and dark mode out-of-the-box without rewriting the Django admin engine. |
| **How does archiving work?** | We use soft-deletion (`is_archived = models.BooleanField(default=False)`). Archived appointments are hidden from active views but preserved for historical reports and can be unarchived anytime. |
| **What happens if a user manipulates query parameters?** | Views use Django ORM parameterized queries (`filter(...)`), fully protecting against SQL injection, and invalid filter keys default safely. |

