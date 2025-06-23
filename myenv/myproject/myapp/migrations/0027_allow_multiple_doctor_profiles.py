from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0026_fix_user_add_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='add',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='doctor_profiles', to='myapp.user'),
        ),
    ] 