from django.contrib import admin

from .models import User, Add, Payment, Appointment
# Register your models here.

admin.site.register(User)
admin.site.register(Add)
admin.site.register(Appointment)
admin.site.register(Payment)