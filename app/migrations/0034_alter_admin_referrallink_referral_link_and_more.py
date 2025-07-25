# Generated by Django 5.1.1 on 2025-05-23 06:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_alter_admin_referrallink_referral_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin_referrallink',
            name='referral_link',
            field=models.CharField(default='c7d7a36654e74156852af523a4cfd4d3', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='assignmentbyprovider',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='app.course'),
        ),
    ]
