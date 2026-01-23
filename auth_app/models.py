from django.db import models
from django.contrib.auth.models import User
import uuid

class UserModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uidb64 = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.user.email