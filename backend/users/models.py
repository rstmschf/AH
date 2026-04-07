import time
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
            return f"{self.username}"


    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        
        suffix = f"_del_{int(time.time())}"
        self.username = f"{self.username}{suffix}"
        self.email = f"{self.email}{suffix}"
        
        self.is_active = False
        self.save()
