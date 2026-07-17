from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """Custom User model for Cookbook Studio."""
    pass

class Profile(models.Model):
    """User Profile for bios, profile images, and followers."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profiles/', default='profiles/default.png', blank=True)
    bio = models.TextField(blank=True, max_length=500)
    follows = models.ManyToManyField('self', symmetrical=False, related_name='followed_by', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def follower_count(self):
        return self.followed_by.count()

    @property
    def following_count(self):
        return self.follows.count()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
