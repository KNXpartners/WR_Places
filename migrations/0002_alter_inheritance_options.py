# Generated by Django 4.0.1 on 2022-01-25 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Places', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inheritance',
            options={'ordering': ['Parent__id']},
        ),
    ]
