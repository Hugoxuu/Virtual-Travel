# Generated by Django 2.1.5 on 2019-04-08 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualTravel', '0005_auto_20190406_2320'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='picture_url',
            field=models.CharField(default='', max_length=500),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='travel',
            name='current_stop',
            field=models.IntegerField(default=0),
        ),
    ]