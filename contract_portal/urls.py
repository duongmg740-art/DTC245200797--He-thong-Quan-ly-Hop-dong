from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django_prometheus.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("contracts.urls")),
]
