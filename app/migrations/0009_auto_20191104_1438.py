# Generated by Django 2.2.6 on 2019-11-04 06:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20191103_1956'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='classroom',
            name='year_end',
        ),
        migrations.RemoveField(
            model_name='classroom',
            name='year_start',
        ),
    ]
