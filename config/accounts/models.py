from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mode = models.CharField(max_length=20, default="secure")  # "secure" or "vulnerable"

    def toggle_mode(self):
        self.mode = "vulnerable" if self.mode == "secure" else "secure"
        self.save()
        return self.mode

class VulnUser(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)  # Stored in plain text!

    def __str__(self):
        return self.username
