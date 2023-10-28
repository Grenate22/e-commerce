from time import sleep
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def notify_customers(messgae):
    print('sending 10k emails')
    print(messgae)
    sleep(10)
    print('Emails were succesfully sent!')
    