# Generated by Django 5.1.1 on 2025-03-28 10:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0018_alter_admin_referrallink_referral_link_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="admin_referrallink",
            name="referral_link",
            field=models.CharField(
                default="b05556e6d6a240c989f63ba67c4fc0d8", max_length=255, unique=True
            ),
        ),
    ]
