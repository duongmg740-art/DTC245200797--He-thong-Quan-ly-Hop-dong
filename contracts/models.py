from django.core.validators import MinValueValidator
from django.db import models


class Counterparty(models.Model):
    name = models.CharField("Tên tổ chức/cá nhân", max_length=200, unique=True)
    contact_name = models.CharField("Người liên hệ", max_length=150, blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Số điện thoại", max_length=30, blank=True)
    notes = models.TextField("Ghi chú", blank=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Bên liên quan"
        verbose_name_plural = "Bên liên quan"

    def __str__(self):
        return self.name


class Contract(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Bản nháp"
        REVIEW = "review", "Đang xem xét"
        ACTIVE = "active", "Đang hiệu lực"
        EXPIRED = "expired", "Đã hết hạn"
        TERMINATED = "terminated", "Đã chấm dứt"

    contract_number = models.CharField("Mã hợp đồng", max_length=50, unique=True)
    title = models.CharField("Tên hợp đồng", max_length=200)
    description = models.TextField("Mô tả", blank=True)
    value = models.DecimalField(
        "Giá trị (VND)",
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    effective_date = models.DateField("Ngày hiệu lực", null=True, blank=True)
    expiry_date = models.DateField("Ngày hết hạn", null=True, blank=True)
    status = models.CharField("Trạng thái", max_length=20, choices=Status.choices, default=Status.DRAFT)
    parties = models.ManyToManyField(Counterparty, through="ContractParty", related_name="contracts")
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Cập nhật lần cuối", auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Hợp đồng"
        verbose_name_plural = "Hợp đồng"

    def __str__(self):
        return f"{self.contract_number} - {self.title}"


class ContractParty(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)
    counterparty = models.ForeignKey(Counterparty, on_delete=models.PROTECT)
    role = models.CharField("Vai trò", max_length=30, default="counterparty")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["contract", "counterparty"], name="unique_contract_counterparty")
        ]
