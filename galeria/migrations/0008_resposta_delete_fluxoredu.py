# Generated by Django 4.2.20 on 2025-03-31 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('galeria', '0007_pergunta_numero_pergunta_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resposta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resposta', models.CharField(blank=True, max_length=50, null=True)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='galeria.paciente')),
                ('pergunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='galeria.pergunta')),
            ],
            options={
                'unique_together': {('paciente', 'pergunta')},
            },
        ),
        migrations.DeleteModel(
            name='FluxoRedu',
        ),
    ]
