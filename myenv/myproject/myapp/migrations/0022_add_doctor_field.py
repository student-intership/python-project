from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0020_auto_20250612_1730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='Doctor',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='Department',
        ),
        migrations.AddField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.add'),
        ),
    ] 