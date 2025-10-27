from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

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
