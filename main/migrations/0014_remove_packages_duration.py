# Generated by Django 4.1.7 on 2023-03-30 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_remove_cartedevent_otp_code_payedevents_otp_code_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='packages',
            name='duration',
        ),
    ]