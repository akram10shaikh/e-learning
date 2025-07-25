# Generated by Django 5.1.1 on 2025-05-23 13:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_assignmentresultbyprovider_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin_referrallink',
            name='referral_link',
            field=models.CharField(default='61cbff2f08f04370ae58a9b32adc0569', max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='Course_Provider_Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Full_Name', models.CharField(max_length=20)),
                ('Mobile_no', models.CharField(max_length=10)),
                ('EmailID', models.EmailField(max_length=255)),
                ('DOB', models.DateField(blank=True, null=True)),
                ('Gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')], default='M', max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
