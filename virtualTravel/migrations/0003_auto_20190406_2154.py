# Generated by Django 2.1.5 on 2019-04-06 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualTravel', '0002_auto_20190406_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travel',
            name='date',
            field=models.DateField(),
        ),
    ]
