from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Events)
admin.site.register(Packages)
admin.site.register(PayedEvents)
admin.site.register(CartedEvent)