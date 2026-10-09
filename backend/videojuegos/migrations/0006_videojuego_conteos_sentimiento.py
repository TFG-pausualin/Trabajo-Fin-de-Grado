from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("videojuegos", "0005_videojuego_numero_resenas"),
    ]

    operations = [
        migrations.AddField(
            model_name="videojuego",
            name="sentimientos_positivos",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="videojuego",
            name="sentimientos_neutrales",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="videojuego",
            name="sentimientos_negativos",
            field=models.PositiveIntegerField(default=0),
        ),
    ]