# Generated by Django 4.2.20 on 2025-04-01 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galeria', '0010_remove_pergunta_tipo_pergunta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resposta',
            name='resposta',
            field=models.BooleanField(default=False),
        ),
    ]
