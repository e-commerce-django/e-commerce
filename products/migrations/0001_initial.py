# Generated by Django 5.0.4 on 2024-04-26 08:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("image_url", models.TextField()),
                ("min_bid_price", models.IntegerField()),
                ("bid_increment", models.IntegerField()),
                ("auction_start_time", models.DateTimeField()),
                ("auction_end_time", models.DateTimeField()),
                ("product_status", models.BooleanField()),
                ("category", models.CharField(max_length=30)),
                ("size", models.IntegerField()),
                ("present_max_bid_price", models.IntegerField(default=None, null=True)),
                ("present_max_bidder_id", models.IntegerField(default=None, null=True)),
                (
                    "seller",
                    models.ForeignKey(
                        db_column="seller_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "product",
            },
        ),
        migrations.CreateModel(
            name="Bid",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bid_result", models.BooleanField()),
                ("bid_price", models.IntegerField()),
                ("bid_time", models.DateTimeField()),
                (
                    "bidder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bids",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bids",
                        to="products.product",
                    ),
                ),
            ],
            options={
                "db_table": "bid",
            },
        ),
    ]
