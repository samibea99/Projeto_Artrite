# Generated by Django 4.2.20 on 2025-03-31 15:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('galeria', '0005_alter_paciente_fase_tratamento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pergunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.CharField(max_length=255)),
                ('fase_tratamento', models.CharField(choices=[('fase1', 'Fase 1 - Início do tratamento'), ('fase1b', 'Fase 1B - Menos de 3 meses de tratamento'), ('fase2', 'Fase 2 - 3 a 6 meses de tratamento'), ('fase3', 'Fase 3 - Mais de 6 meses de tratamento'), ('reducao', 'Redução')], max_length=10)),
                ('tipo_pergunta', models.CharField(choices=[('sim_ou_nao', 'Sim ou Não'), ('texto', 'Texto')], max_length=20)),
                ('pergunta_anterior', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='galeria.pergunta')),
            ],
        ),
    ]
