# Generated by Django 5.2.1 on 2025-06-09 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_add'),
    ]

    operations = [
        migrations.AddField(
            model_name='add',
            name='dprofile',
            field=models.ImageField(default='', upload_to=''),
        ),
    ]
