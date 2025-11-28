from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Extra fields: phone, address, and profile photo.
    """
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    """
    Stores additional info about the user, including simulation mode.
    Default mode = secure.
    """
    MODE_CHOICES = [
        ("secure", "Secure Mode"),
        ("vulnerable", "Vulnerable Mode"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="secure")

    def toggle_mode(self):
        """Switch between secure and vulnerable modes."""
        self.mode = "vulnerable" if self.mode == "secure" else "secure"
        self.save(update_fields=["mode"])
        return self.mode

    def __str__(self):
        return f"{self.user.username} ({self.mode})"


class VulnUser(models.Model):
    """
    Intentionally vulnerable user table for labs:
    - Stores plaintext passwords
    - No built-in validation
    - Exists only for security training
    """
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=100)  # ❌ stored in plain text for demo

    def __str__(self):
        return self.username
