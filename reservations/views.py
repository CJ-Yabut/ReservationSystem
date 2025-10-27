from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from reservations.models import Reservation
from rooms.models import Room
from users.models import UserProfile
import tempfile
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from django.utils import timezone

try:
    from weasyprint import HTML
    PDF_LIB = 'weasyprint'
except (ImportError, OSError):
    HTML = None
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from io import BytesIO
        from django.utils.html import strip_tags
        PDF_LIB = 'reportlab'
    except ImportError:
        PDF_LIB = None


@login_required(login_url='student_login')
def book_room(request):
    if request.method == 'POST':
        room_id = request.POST.get('room')
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        from datetime import datetime, date, time
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError:
            messages.error(request, 'Invalid date or time format.')
            return redirect('book_room')
        
        try:
            room = Room.objects.get(id=room_id)
            
            # Check for conflicts
            conflicts = Reservation.objects.filter(
                room=room,
                date=date,
                status__in=['approved', 'pending']
            ).exclude(
                end_time__lte=start_time
            ).exclude(
                start_time__gte=end_time
            )
            
            if conflicts.exists():
                messages.error(request, 'This time slot is already booked. Please choose another time.')
                return redirect('book_room')

            reason = request.POST.get('reason', '').strip()

            reservation = Reservation.objects.create(
                student=request.user,
                room=room,
                date=date,
                start_time=start_time,
                end_time=end_time,
                reason=reason,
                status='pending'
            )
            
            try:
                html_content = render_to_string('reservations/letter_template.html', {
                    'reservation': reservation,
                    'student': request.user.student,
                    'room': room,
                    'now': timezone.now(),
                })

                if PDF_LIB == 'weasyprint':
                    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                        try:
                            HTML(string=html_content).write_pdf(tmp.name)
                            tmp.seek(0)
                            reservation.letter_file.save(
                                f"reservation_letter_{reservation.id}.pdf",
                                ContentFile(tmp.read()),
                                save=False
                            )
                        finally:
                            # Clean up the temporary file
                            import os
                            try:
                                os.unlink(tmp.name)
                            except:
                                pass
                elif PDF_LIB == 'reportlab':
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = []

                    # Convert HTML to plain text
                    text_content = strip_tags(html_content)
                    story.append(Paragraph(text_content, styles['Normal']))
                    doc.build(story)

                    buffer.seek(0)
                    reservation.letter_file.save(
                        f"reservation_letter_{reservation.id}.pdf",
                        ContentFile(buffer.read()),
                        save=False
                    )
                else:
                    raise Exception("No PDF library available")

                reservation.letter_generated_at = timezone.now()
                reservation.save()
            except Exception as e:
                # log or message if you want — don't stop the reservation creation
                messages.warning(request, f"Reservation created but letter generation failed: {str(e)}")
                

            messages.success(request, 'Room booked successfully! Waiting for admin approval.')
            return redirect('student_reservations')
        except Room.DoesNotExist:
            messages.error(request, 'Room not found.')
        except Exception as e:
            messages.error(request, f'Error booking room: {str(e)}')
    
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'reservations/book_room.html', context)

@login_required(login_url='student_login')
def student_reservations(request):
    reservations = request.user.reservations.all()
    context = {'reservations': reservations}
    return render(request, 'reservations/student_reservations.html', context)

@login_required(login_url='student_login')
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if reservation.student != request.user:
        return HttpResponseForbidden("Access denied")
    
    if reservation.status == 'pending':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'Reservation cancelled.')
    else:
        messages.error(request, 'Only pending reservations can be cancelled.')
    
    return redirect('student_reservations')

@login_required(login_url='admin_login')
def manage_reservations(request):
    user_profile = request.user.profile
    
    if user_profile.role not in ['admin', 'superadmin']:
        return HttpResponseForbidden("Access denied")
    
    # Get reservations based on role
    if user_profile.role == 'superadmin':
        reservations = Reservation.objects.all()
    else:  # admin
        reservations = Reservation.objects.filter(room__admin_type=user_profile.admin_type)
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        reservations = reservations.filter(status=status_filter)
    
    # Calculate stats
    all_reservations = Reservation.objects.all() if user_profile.role == 'superadmin' else Reservation.objects.filter(room__admin_type=user_profile.admin_type)
    pending = all_reservations.filter(status='pending').count()
    approved = all_reservations.filter(status='approved').count()
    rejected = all_reservations.filter(status='rejected').count()
    cancelled = all_reservations.filter(status='cancelled').count()
    
    context = {
        'reservations': reservations,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'cancelled': cancelled,
        'user_profile': user_profile,
        'status_filter': status_filter,
    }
    return render(request, 'reservations/manage_reservations.html', context)

@login_required(login_url='admin_login')
def approve_reservation(request, reservation_id):
    user_profile = request.user.profile
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Superadmins cannot approve
    if user_profile.role == 'superadmin':
        messages.error(request, 'Superadmins cannot approve or reject reservations.')
        return redirect('manage_reservations')

    # Check permission
    if reservation.room.admin_type != user_profile.admin_type:
        return HttpResponseForbidden("Access denied")

    reservation.status = 'approved'
    reservation.rejection_note = None
    reservation.save()

    # Send email notification
    from .utils import send_reservation_notification
    send_reservation_notification(reservation, 'approved')

    messages.success(request, f'Reservation for {reservation.student.username} approved!')
    return redirect('manage_reservations')

@login_required(login_url='admin_login')
def reject_reservation(request, reservation_id):
    user_profile = request.user.profile
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Superadmins cannot reject
    if user_profile.role == 'superadmin':
        messages.error(request, 'Superadmins cannot approve or reject reservations.')
        return redirect('manage_reservations')

    # Check permission
    if reservation.room.admin_type != user_profile.admin_type:
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST':
        rejection_note = request.POST.get('rejection_note', '')
        reservation.status = 'rejected'
        reservation.rejection_note = rejection_note
        reservation.save()

        # Send email notification
        from .utils import send_reservation_notification
        send_reservation_notification(reservation, 'rejected')

        messages.success(request, f'Reservation rejected.')
        return redirect('manage_reservations')

    context = {'reservation': reservation}
    return render(request, 'reservations/reject_reservation.html', context)
