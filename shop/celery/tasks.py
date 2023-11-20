import os
from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone
from datetime import timedelta
import logging
from dotenv import load_dotenv
from django.template.loader import get_template
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
        email.send(fail_silently=True)
    except Exception as e:
        logger.critical(f'Order email not sent.-  {e}')


@shared_task()
def send_cart_abundance_mail():
    try:
        cart_abundance_mail_template = get_template('shop/mail/cart_abundance_mail.html').render()

        user_emails = Cart.objects.filter(
            # created_at__gt=timezone.now() - timedelta(days=5),
            # is_purchased=False
        ).values_list('user__email', flat=True).distinct()

        if user_emails:
            email = EmailMessage(
                'Majestic - Ecommerce site',
                cart_abundance_mail_template,
                os.getenv('SITE_EMAIL_ADDRESS'),
                user_emails
            )

            email.content_subtype = 'html'
            email.send(fail_silently=True)
    except Exception as e:
        logger.warning(f'cart abundance mail did not sent. - {e}')
