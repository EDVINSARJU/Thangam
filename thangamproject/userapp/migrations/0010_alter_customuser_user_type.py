# Generated by Django 4.2.7 on 2024-02-18 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0009_rename_orderitem_orderedproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Admin'), (2, 'Staff'), (3, 'Customer')], default='2'),
        ),
    ]
