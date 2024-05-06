# Generated by Django 5.0.4 on 2024-05-04 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_producto_frecuenciadecompra'),
    ]

    operations = [
        migrations.RenameField(
            model_name='producto',
            old_name='frecuenciaDeCompra',
            new_name='cadaCuantosDias',
        ),
        migrations.AddField(
            model_name='producto',
            name='cantidadPorOrden',
            field=models.IntegerField(default=0),
        ),
    ]