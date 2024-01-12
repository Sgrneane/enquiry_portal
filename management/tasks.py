from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from FQC import settings

@shared_task(bind=True)
def send_notification_mail(self, target_mail,html_content):
        mail_subject = "New Notification Regarding Complaint System!"
        # Create an EmailMessage instance
        email = EmailMessage(
            mail_subject,  # Subject of the email
            html_content,  # HTML content
            settings.EMAIL_HOST_USER,  # Sender's email address
            [target_mail],  # List of recipient email addresses
        )

        # Set the content type to HTML
        email.content_subtype = 'html'
        email.send()

        return "Done"
