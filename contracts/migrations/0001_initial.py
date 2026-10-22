import django.db.models.deletion
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Counterparty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, unique=True, verbose_name="Tên tổ chức/cá nhân")),
                ("contact_name", models.CharField(blank=True, max_length=150, verbose_name="Người liên hệ")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="Email")),
                ("phone", models.CharField(blank=True, max_length=30, verbose_name="Số điện thoại")),
                ("notes", models.TextField(blank=True, verbose_name="Ghi chú")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")),
            ],
            options={
                "verbose_name": "Bên liên quan",
                "verbose_name_plural": "Bên liên quan",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Contract",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("contract_number", models.CharField(max_length=50, unique=True, verbose_name="Mã hợp đồng")),
                ("title", models.CharField(max_length=200, verbose_name="Tên hợp đồng")),
                ("description", models.TextField(blank=True, verbose_name="Mô tả")),
                ("value", models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name="Giá trị (VND)")),
                ("effective_date", models.DateField(blank=True, null=True, verbose_name="Ngày hiệu lực")),
                ("expiry_date", models.DateField(blank=True, null=True, verbose_name="Ngày hết hạn")),
                ("status", models.CharField(choices=[("draft", "Bản nháp"), ("review", "Đang xem xét"), ("active", "Đang hiệu lực"), ("expired", "Đã hết hạn"), ("terminated", "Đã chấm dứt")], default="draft", max_length=20, verbose_name="Trạng thái")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")),
            ],
            options={"verbose_name": "Hợp đồng", "verbose_name_plural": "Hợp đồng", "ordering": ["-updated_at"]},
        ),
        migrations.CreateModel(
            name="ContractParty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(default="counterparty", max_length=30, verbose_name="Vai trò")),
                ("contract", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="contracts.contract")),
                ("counterparty", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="contracts.counterparty")),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(fields=("contract", "counterparty"), name="unique_contract_counterparty")
                ],
            },
        ),
        migrations.AddField(
            model_name="contract",
            name="parties",
            field=models.ManyToManyField(
                related_name="contracts",
                through="contracts.ContractParty",
                to="contracts.counterparty",
            ),
        ),
    ]
