from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("src", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="prescriptionitem",
            constraint=models.UniqueConstraint(
                fields=("prescription", "medicine"),
                name="unique_prescription_medicine_item",
            ),
        ),
    ]
