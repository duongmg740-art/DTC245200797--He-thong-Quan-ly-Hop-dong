from django.contrib import admin

from .models import Contract, ContractParty, Counterparty


class ContractPartyInline(admin.TabularInline):
    model = ContractParty
    extra = 1


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("contract_number", "title", "status", "effective_date", "expiry_date", "updated_at")
    list_filter = ("status",)
    search_fields = ("contract_number", "title", "parties__name")
    inlines = (ContractPartyInline,)


@admin.register(Counterparty)
class CounterpartyAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_name", "email", "phone")
    search_fields = ("name", "contact_name", "email")
