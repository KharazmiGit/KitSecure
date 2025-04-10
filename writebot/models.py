from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    json_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Actions of {self.user.username} at {self.created_at} keycloak_id :  {self.user.keycloak_id}"
