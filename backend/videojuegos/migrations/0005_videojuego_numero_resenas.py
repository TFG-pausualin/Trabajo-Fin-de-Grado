from django.db import migrations, models
from django.db.models import F


def inicializar_numero_resenas(apps, schema_editor):
    Videojuego = apps.get_model("videojuegos", "Videojuego")
    Videojuego.objects.using(schema_editor.connection.alias).update(
        numero_resenas=F("numero_valoraciones")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("videojuegos", "0004_alter_videojuego_tienda"),
    ]

    operations = [
        migrations.AddField(
            model_name="videojuego",
            name="numero_resenas",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Número total de reseñas asociadas al videojuego.",
            ),
        ),
        migrations.RunPython(
            inicializar_numero_resenas,
            migrations.RunPython.noop,
        ),
    ]