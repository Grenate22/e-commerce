from time import sleep
from celery import shared_task

@shared_task
def notify_customers(messgae):
    print('sending 10k emailas')
    print(messgae)
    sleep(10)
    print('email succefully sent')