# Generated by Django 5.1.4 on 2025-01-20 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_leavebalance_carried_forward_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavebalance',
            name='remaining_days',
            field=models.PositiveIntegerField(default=0),
        ),
    ]