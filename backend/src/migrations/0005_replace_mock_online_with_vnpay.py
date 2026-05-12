from django.db import migrations, models


def replace_mock_online_with_vnpay(apps, schema_editor):
    Payment = apps.get_model("src", "Payment")
    Payment.objects.filter(method="MOCK_ONLINE").update(method="VNPAY")


def replace_vnpay_with_mock_online(apps, schema_editor):
    Payment = apps.get_model("src", "Payment")
    Payment.objects.filter(method="VNPAY").update(method="MOCK_ONLINE")


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0004_appointment_waiting_payment_status"),
    ]

    operations = [
        migrations.RunPython(
            replace_mock_online_with_vnpay,
            replace_vnpay_with_mock_online,
        ),
        migrations.AlterField(
            model_name="payment",
            name="method",
            field=models.CharField(
                choices=[("CASH", "Cash"), ("VNPAY", "VNPAY")],
                default="VNPAY",
                max_length=20,
            ),
        ),
    ]
