from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(City)
admin.site.register(Quiz)
admin.site.register(Picture)
admin.site.register(Travel)
admin.site.register(Profile)
admin.site.register(Site)

