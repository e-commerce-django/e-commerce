# Generated by Django 5.0.4 on 2024-06-17 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='billing_key',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]