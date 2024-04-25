# Generated by Django 5.0.4 on 2024-04-25 07:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_product_seller'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='seller',
            field=models.ForeignKey(db_column='seller_id', on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.user'),
        ),
    ]
