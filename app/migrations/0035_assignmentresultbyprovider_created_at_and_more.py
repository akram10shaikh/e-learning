# Generated by Django 5.1.1 on 2025-05-23 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_alter_admin_referrallink_referral_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignmentresultbyprovider',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='admin_referrallink',
            name='referral_link',
            field=models.CharField(default='c85f4e7d63264fa79278f47e37a1e3ac', max_length=255, unique=True),
        ),
    ]
