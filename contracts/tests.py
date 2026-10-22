from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Contract, Counterparty


class ContractWorkflowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="operator", password="Strong-test-password-42!")
        self.party = Counterparty.objects.create(name="Công ty Đối tác")

    def test_contract_pages_require_login(self):
        response = self.client.get(reverse("contracts:list"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('contracts:list')}")

    def test_create_contract_with_parties_and_status(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("contracts:create"),
            {
                "contract_number": "HD-2026-001",
                "title": "Hợp đồng dịch vụ",
                "status": Contract.Status.REVIEW,
                "parties": [self.party.pk],
            },
        )
        contract = Contract.objects.get(contract_number="HD-2026-001")
        self.assertRedirects(response, reverse("contracts:detail", args=[contract.pk]))
        self.assertEqual(contract.status, Contract.Status.REVIEW)
        self.assertEqual(list(contract.parties.all()), [self.party])

    def test_status_filter(self):
        self.client.force_login(self.user)
        Contract.objects.create(contract_number="HD-1", title="Bản nháp")
        Contract.objects.create(contract_number="HD-2", title="Có hiệu lực", status=Contract.Status.ACTIVE)
        response = self.client.get(reverse("contracts:list"), {"status": Contract.Status.ACTIVE})
        self.assertEqual([contract.contract_number for contract in response.context["contracts"]], ["HD-2"])

    def test_invalid_contract_period_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("contracts:create"),
            {
                "contract_number": "HD-2026-002",
                "title": "Hợp đồng sai thời hạn",
                "status": Contract.Status.DRAFT,
                "effective_date": "2026-12-31",
                "expiry_date": "2026-01-01",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contract.objects.filter(contract_number="HD-2026-002").exists())
        self.assertIn("expiry_date", response.context["form"].errors)
