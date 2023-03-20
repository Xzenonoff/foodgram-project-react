# Generated by Django 4.1.7 on 2023-03-20 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0006_rename_measure_unit_ingredient_measurement_unit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ingredientquantity",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredients",
                to="api.ingredient",
            ),
        ),
        migrations.AlterField(
            model_name="ingredientquantity",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recipes",
                to="api.recipe",
            ),
        ),
    ]
