# Generated by Django 2.1.5 on 2019-04-06 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualTravel', '0003_auto_20190406_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travel',
            name='date',
            field=models.DateTimeField(),
        ),
    ]