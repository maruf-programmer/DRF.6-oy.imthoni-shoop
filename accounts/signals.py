from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from cart.models import Cart
from wishlist.models import Wishlist

@receiver(post_save, sender=CustomUser)
def create_user_cart_and_wishlist(sender, instance, created, **kwargs):
    if created:
        Cart.objects.get_or_create(user=instance)
        Wishlist.objects.get_or_create(user=instance)