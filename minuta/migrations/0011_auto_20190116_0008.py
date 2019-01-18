# Generated by Django 2.1.4 on 2019-01-16 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minuta', '0010_movimiento'),
    ]

    operations = [
        migrations.AddField(
            model_name='hora',
            name='cantidad_horas',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movimiento',
            name='descripcion',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='movimiento',
            name='monto',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='proyecto',
            name='horas_presupuestada',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
    ]