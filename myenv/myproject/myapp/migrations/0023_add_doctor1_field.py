from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0022_add_doctor_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='add',
            name='doctor1',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.user'),
        ),
    ] 