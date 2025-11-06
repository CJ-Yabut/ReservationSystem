from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Reservation
import os

def send_reservation_notification(reservation, action):
    """
    Send email notification to student about reservation status change.

    Args:
        reservation: Reservation instance
        action: 'approved' or 'rejected'
    """
    subject = f"Reservation {action.capitalize()}"
    recipient = reservation.student.email

    # Prepare context for email template
    context = {
        'reservation': reservation,
        'student': reservation.student,
        'room': reservation.room,
        'action': action,
        'status': reservation.get_status_display(),
    }

    # Render email content
    html_message = render_to_string('reservations/reservation_notification.html', context)
    plain_message = f"""
    Dear {reservation.student.get_full_name() or reservation.student.username},

    Your reservation for {reservation.room.name} on {reservation.date} from {reservation.start_time} to {reservation.end_time} has been {action}.

    Status: {reservation.get_status_display()}

    {'Rejection Note: ' + reservation.rejection_note if reservation.rejection_note else ''}

    Thank you for using our reservation system.

    Best regards,
    Reservation System Team
    """

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error if needed
        print(f"Failed to send email: {e}")
        return False


def generate_approval_code():
    """
    Generate a unique 8-character random approval code in format APPRXXXX.
    APPR + 4 random alphanumeric characters (uppercase letters and digits)

    Returns:
        str: Unique 8-character approval code
    """
    import random
    import string

    while True:
        # Generate 4 random alphanumeric characters (uppercase)
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        approval_code = f"APPR{random_chars}"

        # Ensure uniqueness
        if not Reservation.objects.filter(approval_code=approval_code).exists():
            return approval_code


def send_reservation_notification_with_attachment(reservation, action):
    """
    Send email notification to student about reservation status change with PDF attachment.

    Args:
        reservation: Reservation instance
        action: 'approved' or 'rejected'
    """
    subject = f"Reservation {action.capitalize()}"
    recipient = reservation.student.email

    # Prepare context for email template
    context = {
        'reservation': reservation,
        'student': reservation.student,
        'room': reservation.room,
        'action': action,
        'status': reservation.get_status_display(),
    }

    # Render email content
    html_message = render_to_string('reservations/reservation_notification.html', context)
    plain_message = f"""
    Dear {reservation.student.get_full_name() or reservation.student.username},

    Your reservation for {reservation.room.name} on {reservation.date} from {reservation.start_time} to {reservation.end_time} has been {action}.

    Status: {reservation.get_status_display()}

    {'Rejection Note: ' + reservation.rejection_note if reservation.rejection_note else ''}

    Thank you for using our reservation system.

    Best regards,
    Reservation System Team
    """

    try:
        # Create email with HTML content and attachment
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.content_subtype = "html"  # Set content type to HTML

        # Attach PDF if available and action is 'approved'
        if action == 'approved' and reservation.letter_file:
            try:
                with reservation.letter_file.open('rb') as pdf_file:
                    email.attach(
                        f"approval_letter_{reservation.approval_code}.pdf",
                        pdf_file.read(),
                        'application/pdf'
                    )
            except Exception as e:
                print(f"Failed to attach PDF: {e}")

        email.send(fail_silently=False)
        return True
    except Exception as e:
        # Log the error if needed
        print(f"Failed to send email: {e}")
        return False
