# Generated by Django 3.2.2 on 2021-05-15 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airlinecontroller', '0003_flightcrew_crew_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='airplane',
            name='plane_name',
            field=models.CharField(default='', max_length=64),
        ),
        migrations.AlterField(
            model_name='flightcrew',
            name='crew_name',
            field=models.CharField(default='', max_length=64),
        ),
    ]
