from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import User  # Ensure correct import path


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    list_display = ['username', 'email', 'is_admin']
    list_filter = ['is_admin']

    fieldsets = [
        (None, {'fields': ['username', 'password']}),
        ('Personal info', {'fields': ['email', 'personnel_code']}),
        ('Permissions', {'fields': ['is_admin', 'is_active']}),
    ]

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                'classes': ['wide'],
                'fields': ['username', 'email', 'personnel_code', 'password1', 'password2'],
            },
        ),
    ]

    search_fields = ['username', 'email', 'personnel_code']
    ordering = ['username']
    filter_horizontal = []




# Register the new UserAdmin
admin.site.register(User, UserAdmin)

