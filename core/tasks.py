from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import get_template

@shared_task
def send_welcome_email(user_email):
    subject = 'Confirmation instructions for Grenate store'

    html_message = get_template('core/welcome_email.html').render()

    email = EmailMessage(
        subject,
        to=[user_email],
    )

    email.attach_file(html_message, 'text/html')

    email.send()
