from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0025_payment'),
    ]

    operations = [
        # Add the user field as nullable first
        migrations.AddField(
            model_name='add',
            name='user',
            field=models.OneToOneField(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='doctor_profile', to='myapp.user'),
        ),
        # Update User model's usertype choices
        migrations.AlterField(
            model_name='user',
            name='usertype',
            field=models.CharField(choices=[('Patient', 'Patient'), ('Doctor', 'Doctor')], default='Patient', max_length=20),
        ),
    ] 