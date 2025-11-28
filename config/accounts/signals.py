from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile

User = settings.AUTH_USER_MODEL  # safer than importing auth.User directly


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Ensure each User always has an associated UserProfile.
    """
    if created:
        # New user → create associated profile
        UserProfile.objects.create(user=instance)
    else:
        # Existing user → save profile if it exists
        if hasattr(instance, "profile"):
            instance.profile.save()
