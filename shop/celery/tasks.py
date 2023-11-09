import os
from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import timedelta
import logging
from dotenv import load_dotenv

from shop.models import Cart

logger = logging.getLogger('django')
load_dotenv()


@shared_task()
def send_order_details_mail(user_email, body):
    try:
        email = EmailMessage(
            'Majestic - Ecommerce site',
            body,
            os.getenv('SITE_EMAIL_ADDRESS'),
            [user_email]
        )

        email.content_subtype = 'html'
        email.send(fail_silently=False)
    except Exception as e:
        logger.critical(f'Order email not sent.-  {e}')


@shared_task()
def send_cart_abundance_mail():
    try:
        abundant_cart_users = Cart.objects.filter(
            created_at__gt=timezone.now() - timedelta(days=5),
            is_purchased=True
        ).values('user').distinct()

        if abundant_cart_users:
            email = EmailMessage(
                'Majestic - Ecommerce site',
                os.getenv('SITE_EMAIL_ADDRESS'),
            )

            email.content_subtype = 'html'
            email.send(fail_silently=False)
    except Exception as e:
        logger.warning(f'cart abundance mail did not sent. - {e}')
