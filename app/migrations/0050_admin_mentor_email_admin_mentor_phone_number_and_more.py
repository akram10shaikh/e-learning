# Generated by Django 5.1.1 on 2025-05-27 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0049_rename_marketer_admin_payment_affiliate_marketer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin_mentor',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='admin_mentor',
            name='phone_number',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='admin_referrallink',
            name='referral_link',
            field=models.CharField(default='ca9af686537941f09856eca078acbee4', max_length=255, unique=True),
        ),
    ]
