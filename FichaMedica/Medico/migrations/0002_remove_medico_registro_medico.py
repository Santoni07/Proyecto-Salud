# Generated by Django 5.1.1 on 2024-10-28 23:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Medico', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='medico',
            name='registro_medico',
        ),
    ]
