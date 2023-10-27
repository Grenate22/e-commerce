from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Customer,Order

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_new_user(sender, **kwargs):
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])

    
@receiver(post_save, sender=Order)
def upgrade_membership(sender, instance, created , **kwargs):
    if created:
        customer = instance.customer
        order_count = customer.order_set.count()
        if order_count > 20 and customer.membership != 'S':
            customer.membership = 'S'
            customer.save()
        elif order_count > 30  and customer.membership != 'G':
            customer.membership = 'G'
            customer.save()


    
