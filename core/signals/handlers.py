from django.dispatch import receiver
from storre.signals import order_created

@receiver(order_created)
def on_order_created(sender, **kwargs):
    print(kwargs['order'])
