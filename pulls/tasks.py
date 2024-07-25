from django.conf import settings
from django.core import mail
from .models import Users
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from celery import shared_task


@shared_task
def send_email_message(subject,header_from, template_name, user_id, ctx,simple):
    html_message = render_to_string(template_name,ctx)
    plain_message = strip_tags(html_message)
    mail.send_mail(
        subject=subject,
        message=plain_message,
        from_email=header_from,
        recipient_list=[Users.objects.get(id_user=user_id).users_mail if simple else user_id],
        fail_silently=False,
        html_message=html_message,
    )