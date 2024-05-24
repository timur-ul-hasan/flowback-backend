# Generated by Django 4.2.7 on 2024-05-24 08:49

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0040_poll_finalization_period_start_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='approval_minimum',
            field=models.PositiveIntegerField(default=51, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='poll',
            name='finalization_period',
            field=models.PositiveIntegerField(default=3, help_text='Finalization period in days', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)]),
        ),
        migrations.AlterField(
            model_name='poll',
            name='quorum',
            field=models.IntegerField(default=51, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)]),
        ),
    ]
