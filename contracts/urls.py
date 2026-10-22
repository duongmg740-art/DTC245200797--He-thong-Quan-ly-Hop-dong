from django.urls import path

from . import views

app_name = "contracts"

urlpatterns = [
    path("", views.contract_list, name="list"),
    path("contracts/new/", views.contract_create, name="create"),
    path("contracts/<int:pk>/", views.contract_detail, name="detail"),
    path("contracts/<int:pk>/edit/", views.contract_update, name="edit"),
    path("parties/", views.counterparty_list, name="parties"),
    path("parties/new/", views.counterparty_create, name="party-create"),
]
