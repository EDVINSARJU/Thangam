# Generated by Django 4.2.7 on 2024-01-30 06:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0006_cartitem'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
