# Generated by Django 5.0.6 on 2024-05-14 20:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_notificaciones_estadopedido'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportantStuff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_sid', models.CharField(max_length=50)),
                ('auth_token', models.CharField(max_length=50)),
            ],
        ),
    ]
