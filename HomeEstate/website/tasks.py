from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Inquiry


@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_inquiry_notification(inquiry_id):
    inquiry = Inquiry.objects.select_related('property__owner', 'requester').get(pk=inquiry_id)
    send_mail(
        subject=f'New inquiry for {inquiry.property.title}',
        message=(
            f'{inquiry.requester.email} sent an inquiry:\n\n'
            f'{inquiry.message}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[inquiry.property.owner.email],
    )
