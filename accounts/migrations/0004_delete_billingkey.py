# Generated by Django 5.0.4 on 2024-06-19 01:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_user_billing_key_billingkey'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BillingKey',
        ),
    ]
