# Generated by Django 2.1.5 on 2019-04-06 23:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('virtualTravel', '0004_auto_20190406_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='travel',
            name='current_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='current_travel', to='virtualTravel.Profile', unique=True),
        ),
    ]
