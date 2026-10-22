from django import forms

from .models import Contract, Counterparty


class ContractForm(forms.ModelForm):
    parties = forms.ModelMultipleChoiceField(
        label="Bên liên quan",
        queryset=Counterparty.objects.order_by("name"),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Contract
        fields = (
            "contract_number",
            "title",
            "description",
            "value",
            "effective_date",
            "expiry_date",
            "status",
        )
        widgets = {
            "effective_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "value": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("effective_date")
        expiry_date = cleaned_data.get("expiry_date")
        if start_date and expiry_date and expiry_date < start_date:
            self.add_error("expiry_date", "Ngày hết hạn không được trước ngày hiệu lực.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["parties"].initial = self.instance.parties.all()

    def save(self, commit=True):
        contract = super().save(commit=False)
        if commit:
            contract.save()
            self.save_m2m()
        return contract

    def _save_m2m(self):
        from .models import ContractParty

        if self.instance.pk:
            contract = self.instance
            ContractParty.objects.filter(contract=contract).delete()
            ContractParty.objects.bulk_create(
                [
                    ContractParty(contract=contract, counterparty=party)
                    for party in self.cleaned_data["parties"]
                ]
            )


class CounterpartyForm(forms.ModelForm):
    class Meta:
        model = Counterparty
        fields = ("name", "contact_name", "email", "phone", "notes")
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
