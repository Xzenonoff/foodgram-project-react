# Generated by Django 4.1.7 on 2023-03-16 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"ordering": ("id",)},
        ),
    ]