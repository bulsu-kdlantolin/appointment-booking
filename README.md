# 📅 Appointment Booking System

A modern, responsive appointment booking and scheduling web application built with **Django** and styled with **Django Unfold** (Tailwind CSS, Alpine.js, and Material Symbols).

Designed for service-oriented businesses to easily schedule, track, manage, and archive client appointments with a clean public interface and an intuitive, modern administration panel.

---

## ✨ Features

### 👤 Public & Client Management
- **Appointment Scheduling**: Book appointments with automatic validation preventing past-date scheduling and scheduling conflicts.
- **Search & Filtering**: Search appointments by client name and filter by status (`Scheduled`, `Completed`, `Cancelled`).
- **Archive & History**: Archive completed/past appointments with soft-deletion and easy unarchiving support.
- **Responsive UI**: Fully mobile-friendly and clean interface for booking on any device.

### 🛠️ Modern Admin Dashboard (Django Unfold)
- **Tailwind & Alpine.js Interface**: Clean, modern aesthetics replacing the legacy Django admin look.
- **Custom Sidebar Navigation**: Grouped hierarchical navigation with quick access to Appointments, Clients, Services, Users, and Groups.
- **Related Widget 3-Dots Menu**: Easily **Add**, **Change**, **View**, and **Delete** related records (Clients and Services) directly from appointment forms via smooth popups with automatic state syncing.
- **Smart Date & Time Picker**: Integrated Flatpickr datetime picker with 12-hour AM/PM toggling and automatic error dismissal.
- **Scrollable Recent Actions**: The dashboard action history automatically becomes scrollable when reaching screen height to prevent unnecessary full-page vertical scrolling.
- **Permissions Filter**: Refined dual-listbox permissions selector that blends seamlessly into the modern dark/light UI.

---

## 🚀 Tech Stack

- **Backend**: Python 3.10+ (tested on Python 3.12 & 3.13), Django 6.1+
- **Admin UI**: [Django Unfold](https://github.com/unfoldadmin/django-unfold) (Tailwind CSS, Alpine.js, Material Symbols)
- **Database**: SQLite (default, zero-configuration) or PostgreSQL/MySQL
- **Frontend Assets**: Custom vanilla JS, Flatpickr datetime picker, Inter & Plus Jakarta Sans typography

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your machine:
- **Python**: Version 3.10 or higher ([Download Python](https://www.python.org/downloads/))
- **Git**: ([Download Git](https://git-scm.com/))

---

## ⚡ Quickstart Setup Guide

Follow these simple steps to set up and run the project locally on your device.

### 1. Clone the Repository

```bash
git clone https://github.com/bulsu-kdlantolin/appointment-booking.git
cd appointment-booking
```

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> *Note for PowerShell users:* If you encounter an execution policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then re-run the activation script.

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

Install all required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 4. Run Database Migrations

Apply the database migrations to set up the SQLite database schema:

```bash
python manage.py migrate
```

---

### 5. Load Initial Sample Data (Recommended)

Populate your database with sample services, clients, and appointments in one command:

```bash
python manage.py loaddata sample_data
```

---

### 6. Create an Admin Account (Superuser)

Create a superuser to access the Django Unfold administrative dashboard:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter your desired username, email, and password.

---

### 7. Start the Development Server

Start Django's built-in local development server:

```bash
python manage.py runserver
```

> **Tip:** If port 8000 is already in use on your computer, you can run on a different port:
> ```bash
> python manage.py runserver 8080
> ```

Once running, you can access the application at:
- **Public Appointment Booking**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Dashboard**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Running Automated Tests

The project includes a comprehensive unit and integration test suite covering model constraints, `__str__()` methods, `select_related` query optimizations, conflict prevention, archiving workflows, form validations, permissions & groups enforcement, and public view flows.

To run the complete test suite:

```bash
python manage.py test
```

Expected output:
```text
Creating test database for alias 'default'...
.............................
----------------------------------------------------------------------
Ran 29 tests in 0.125s

OK
```

---

## 📁 Project Structure

```text
appointment-booking/
├── appointments/              # Core appointment booking application
│   ├── migrations/            # Database migrations
│   ├── templates/             # Public & Unfold custom templates
│   │   ├── appointments/      # Client-facing appointment templates
│   │   └── unfold/            # Customizations for Unfold admin layout & widgets
│   ├── admin.py               # Unfold admin registrations & customizations
│   ├── forms.py               # Appointment creation & editing forms
│   ├── middleware.py          # Custom middleware (e.g., custom 404 handler)
│   ├── models.py              # Appointment, Client, and Service data models
│   ├── tests.py               # Comprehensive unit and integration test suite
│   ├── urls.py                # Public URL routing
│   └── views.py               # View controllers for appointments
├── config/                    # Django project configuration
│   ├── settings.py            # Main settings, Unfold navigation & sidebar setup
│   ├── urls.py                # Root URL configuration
│   └── wsgi.py                # WSGI entry point
├── static/                    # Static assets
│   ├── css/
│   │   └── admin_fonts.css    # Typography, sidebar & modern widget styles
│   └── js/                    # Admin enhancers (datetime, 3-dots sync, permissions)
├── db.sqlite3                 # Local SQLite database (created after migrate)
├── manage.py                  # Django CLI entry point
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation & setup instructions
```

---

## ⚙️ Key Configuration Highlights

- **Custom Unfold Sidebar**: Defined in `config/settings.py` under the `UNFOLD["SIDEBAR"]` dictionary. You can easily add, rename, or reorder menu items and icons.
- **Frame Options for Popups**: `X_FRAME_OPTIONS = 'SAMEORIGIN'` is configured in `settings.py` to allow secure in-modal iframe rendering for related widget popups.
- **Material Symbols**: Integrated Google Material Symbols Outlined for crisp, consistent iconography across both light and dark modes.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - feel free to use and modify it for your personal or commercial projects.

