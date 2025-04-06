from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, username, personnel_code=None, email=None,
                    password=None, **extra_fields):
        if not username:
            raise ValueError("Users must have a username")

        # Normalize email (convert to lowercase)
        email = self.normalize_email(email) if email else None

        user = self.model(
            username=username,
            personnel_code=personnel_code,
            email=email,
            **extra_fields  # Capture any additional fields sent by Keycloak
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Superuser must have a username")

        # Ensure 'is_admin' is set to True for superusers
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_active', True)

        user = self.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# user model
class User(AbstractBaseUser):
    username = models.CharField(max_length=200, unique=True, verbose_name='Username')
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        null=True,
        blank=True,
    )

    email_verified = models.BooleanField(default=False, null=True, blank=True)  # Add this field
    name = models.CharField(max_length=255, null=True, blank=True)  # Add this field
    personnel_code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"  # Must match the field name
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True  # Simplified permissions logic

    def has_module_perms(self, app_label):
        return True  # Simplified module-level permissions logic

    @property
    def is_staff(self):
        return self.is_admin
