# Generated by Django 5.1.1 on 2025-05-27 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0048_admin_payment_marketer_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='admin_payment',
            old_name='marketer',
            new_name='affiliate_marketer',
        ),
        migrations.AlterField(
            model_name='admin_referrallink',
            name='referral_link',
            field=models.CharField(default='4735ecb2c78b41bdbefe5ddd1e6c8b2f', max_length=255, unique=True),
        ),
    ]
