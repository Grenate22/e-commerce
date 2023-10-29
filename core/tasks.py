from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import get_template
from templated_mail.mail import BaseEmailMessage

@shared_task
def send_welcome_email(user_email,user_firstname):
    message = BaseEmailMessage(
        template_name = 'core/welcome_email.html',
        context = {'name':user_firstname }
    )
    message.send([user_email])