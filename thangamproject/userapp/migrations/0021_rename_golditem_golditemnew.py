# Generated by Django 4.2.7 on 2024-03-07 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0020_golditem'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GoldItem',
            new_name='GoldItemNew',
        ),
    ]