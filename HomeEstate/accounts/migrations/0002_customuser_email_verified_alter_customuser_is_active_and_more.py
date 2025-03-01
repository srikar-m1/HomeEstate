# Generated by Django 5.1.5 on 2025-01-27 14:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='mobile_num',
            field=models.CharField(max_length=10, validators=[django.core.validators.RegexValidator(message='Mobile number must be exactly 10 digits.', regex='^\\d{10}$')]),
        ),
    ]
