# Generated by Django 5.2.1 on 2025-06-09 14:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_add_dprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='add',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.user'),
        ),
    ]
