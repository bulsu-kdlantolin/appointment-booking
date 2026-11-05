from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve
from appointments.views import custom_404

handler404 = "appointments.views.custom_404"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("404/", custom_404, name="custom_404"),
    path("", include("appointments.urls")),
]

urlpatterns += [
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {"document_root": settings.STATIC_ROOT},
    ),
]
