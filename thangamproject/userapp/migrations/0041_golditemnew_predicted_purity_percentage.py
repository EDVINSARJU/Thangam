# Generated by Django 4.2.7 on 2024-04-13 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0040_product_predicted_purity_percentage'),
    ]

    operations = [
        migrations.AddField(
            model_name='golditemnew',
            name='predicted_purity_percentage',
            field=models.FloatField(default=0.0),
        ),
    ]