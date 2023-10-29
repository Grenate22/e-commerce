from django.dispatch import receiver
from storre.signals import order_created
from djoser.signals import user_registered


@receiver(order_created)
def on_order_created(sender, **kwargs):
    print(kwargs['order'])


@receiver(user_registered)
def send_welcome_email(sender, user, request, **kwargs):
    from ..tasks import send_welcome_email
    send_welcome_email.delay(user.email,user.first_name)