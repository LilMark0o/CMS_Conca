# Generated by Django 5.0.4 on 2024-05-04 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_alter_producto_fecha_registro_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='fecha_registro',
            field=models.DateField(auto_now_add=True),
        ),
    ]