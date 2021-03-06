# Generated by Django 2.1.5 on 2019-04-23 23:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('virtualTravel', '0011_auto_20190423_2300'),
    ]

    operations = [
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='')),
                ('content_type', models.CharField(max_length=50)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='virtualTravel.City')),
            ],
        ),
    ]
