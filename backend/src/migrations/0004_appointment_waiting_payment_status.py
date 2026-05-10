from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0003_payment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("CONFIRMED", "Confirmed"),
                    ("CHECKED_IN", "Checked In"),
                    ("IN_PROGRESS", "In Progress"),
                    ("WAITING_PAYMENT", "Waiting Payment"),
                    ("COMPLETED", "Completed"),
                    ("CANCELLED", "Cancelled"),
                    ("NO_SHOW", "No Show"),
                ],
                default="PENDING",
                max_length=20,
            ),
        ),
    ]
