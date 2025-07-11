# Generated by Django 5.0.1 on 2025-07-03 10:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_is_approved_emailverification"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountDeactivation",
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
                (
                    "reason",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("not_using", "Not using the platform anymore"),
                            ("privacy_concerns", "Privacy concerns"),
                            ("found_alternative", "Found an alternative platform"),
                            ("temporary_break", "Taking a temporary break"),
                            ("technical_issues", "Technical issues"),
                            ("other", "Other reason"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "feedback",
                    models.TextField(
                        blank=True,
                        help_text="User feedback about deactivation",
                        max_length=500,
                    ),
                ),
                ("deactivated_at", models.DateTimeField(auto_now_add=True)),
                (
                    "can_reactivate",
                    models.BooleanField(
                        default=True, help_text="Whether user can request reactivation"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="deactivation",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "accounts_accountdeactivation",
                "ordering": ["-deactivated_at"],
            },
        ),
        migrations.CreateModel(
            name="ReactivationRequest",
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
                ("email", models.EmailField(max_length=254)),
                ("message", models.TextField(blank=True, max_length=500)),
                ("requested_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending Review"),
                            ("approved", "Approved"),
                            ("denied", "Denied"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("admin_notes", models.TextField(blank=True)),
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_reactivations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "accounts_reactivationrequest",
                "ordering": ["-requested_at"],
            },
        ),
    ]
