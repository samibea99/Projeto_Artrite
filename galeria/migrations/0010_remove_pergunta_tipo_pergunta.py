# Generated by Django 4.2.20 on 2025-03-31 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('galeria', '0009_alter_resposta_resposta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pergunta',
            name='tipo_pergunta',
        ),
    ]
