# Generated by Django 4.2.20 on 2025-03-31 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('galeria', '0006_pergunta'),
    ]

    operations = [
        migrations.AddField(
            model_name='pergunta',
            name='numero_pergunta',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='pergunta',
            unique_together={('numero_pergunta', 'fase_tratamento')},
        ),
    ]
