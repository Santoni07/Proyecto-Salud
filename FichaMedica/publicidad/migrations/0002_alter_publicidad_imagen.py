# Generated by Django 5.1.1 on 2024-10-11 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publicidad', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicidad',
            name='imagen',
            field=models.ImageField(upload_to='media/publicidades'),
        ),
    ]
