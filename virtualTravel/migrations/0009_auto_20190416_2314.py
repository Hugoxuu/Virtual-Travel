# Generated by Django 2.1.5 on 2019-04-16 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualTravel', '0008_site'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
