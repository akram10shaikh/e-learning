# Generated by Django 5.1.1 on 2025-06-04 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0058_alter_admin_referrallink_referral_link_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin_referrallink',
            name='referral_link',
            field=models.CharField(default='5560e0ac495e4baba83a8b8475d69f05', max_length=255, unique=True),
        ),
    ]
