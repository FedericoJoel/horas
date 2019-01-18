# Generated by Django 2.1.4 on 2019-01-06 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('minuta', '0005_auto_20181213_0218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asistente',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='empleados', to='minuta.Empresa'),
        ),
        migrations.AlterField(
            model_name='definicion',
            name='tema',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='definiciones', to='minuta.Tema'),
        ),
        migrations.AlterField(
            model_name='minuta',
            name='proyecto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='minutas', to='minuta.Proyecto'),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proyectos', to='minuta.Empresa'),
        ),
        migrations.AlterField(
            model_name='tema',
            name='minuta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='temas', to='minuta.Minuta'),
        ),
    ]