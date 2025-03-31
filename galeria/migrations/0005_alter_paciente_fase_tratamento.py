# Generated by Django 4.2.20 on 2025-03-30 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galeria', '0004_rename_fluxoreducao_fluxoredu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paciente',
            name='fase_tratamento',
            field=models.CharField(choices=[('fase1', 'Fase 1 - Início do tratamento'), ('fase1b', 'Fase 1B - Menos de 3 meses de tratamento'), ('fase2', 'Fase 2 - 3 a 6 meses de tratamento'), ('fase3', 'Fase 3 - Mais de 6 meses de tratamento'), ('reducao', 'Redução')], max_length=10),
        ),
    ]
