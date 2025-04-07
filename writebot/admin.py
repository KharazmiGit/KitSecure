from django.contrib import admin
from . import models

@admin.register(models.UserAction)
class UserActionsAdmin(admin.ModelAdmin):
    pass 
