# Generated by Django 5.1.1 on 2025-05-22 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_alter_admin_referrallink_referral_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin_referrallink',
            name='referral_link',
            field=models.CharField(default='322b8eb4a42447fd912d1ae28f2797c5', max_length=255, unique=True),
        ),
    ]
