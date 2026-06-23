from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    cargo = models.CharField(max_length=100, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username
