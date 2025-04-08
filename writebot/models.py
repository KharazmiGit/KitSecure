from django.db import models
import json 
from django.db import models
from django.contrib.auth import get_user_model

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from io import BytesIO
from openpyxl import Workbook
from django.http import HttpResponse

User = get_user_model()


class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    json_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Actions of {self.user.username} at {self.created_at}"

