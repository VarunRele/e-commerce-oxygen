# Generated by Django 5.2.4 on 2025-07-12 08:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='address',
            unique_together=set(),
        ),
    ]
