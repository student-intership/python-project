from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0023_add_doctor1_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add',
            name='doctor1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='doctor_profile', to='myapp.user'),
        ),
    ] 