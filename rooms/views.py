from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from rooms.models import Room, Campus, AdminType
from reservations.models import Reservation
from users.models import UserProfile
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta

@login_required(login_url='admin_login')
def admin_dashboard(request):
    user_profile = request.user.profile
    
    # Check if user is admin or superadmin
    if user_profile.role not in ['admin', 'superadmin']:
        return HttpResponseForbidden("Access denied")
    
    # Get rooms based on role
    if user_profile.role == 'superadmin':
        rooms = Room.objects.all()
        reservations = Reservation.objects.all()
    else:  # admin
        rooms = Room.objects.filter(admin_type=user_profile.admin_type)
        reservations = Reservation.objects.filter(room__admin_type=user_profile.admin_type)
    
    # Calculate stats
    pending_count = reservations.filter(status='pending').count()
    approved_count = reservations.filter(status='approved').count()
    rejected_count = reservations.filter(status='rejected').count()
    cancelled_count = reservations.filter(status='cancelled').count()
    
    # Get recent pending reservations (first 5)
    recent_pending = reservations.filter(status='pending')[:5]
    
    context = {
        'user_profile': user_profile,
        'rooms': rooms,
        'reservations': reservations,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'cancelled_count': cancelled_count,
        'recent_pending': recent_pending,
        'total_reservations': reservations.count(),
    }
    return render(request, 'rooms/admin_dashboard.html', context)

@login_required(login_url='admin_login')
def add_room(request):
    user_profile = request.user.profile
    
    # Only regular admins can add rooms
    if user_profile.role != 'admin':
        return HttpResponseForbidden("Only admins can add rooms")
    
    if request.method == 'POST':
        campus_id = request.POST.get('campus')
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        description = request.POST.get('description')
        
        try:
            campus = Campus.objects.get(id=campus_id)
            room = Room.objects.create(
                campus=campus,
                admin_type=user_profile.admin_type,
                name=name,
                capacity=capacity,
                description=description
            )
            messages.success(request, f'Room "{name}" added successfully!')
            return redirect('admin_dashboard')
        except Campus.DoesNotExist:
            messages.error(request, 'Campus not found.')
        except Exception as e:
            messages.error(request, f'Error adding room: {str(e)}')
    
    campuses = Campus.objects.all()
    context = {'campuses': campuses}
    return render(request, 'rooms/add_room.html', context)

@login_required(login_url='admin_login')
def edit_room(request, room_id):
    user_profile = request.user.profile
    room = get_object_or_404(Room, id=room_id)
    
    # Check permission
    if user_profile.role == 'admin' and room.admin_type != user_profile.admin_type:
        return HttpResponseForbidden("Access denied")
    elif user_profile.role == 'student':
        return HttpResponseForbidden("Access denied")
    
    if request.method == 'POST':
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        description = request.POST.get('description')
        
        try:
            room.name = name
            room.capacity = capacity
            room.description = description
            room.save()
            messages.success(request, f'Room "{name}" updated successfully!')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error updating room: {str(e)}')
    
    campuses = Campus.objects.all()
    context = {
        'room': room,
        'campuses': campuses,
    }
    return render(request, 'rooms/edit_room.html', context)

@login_required(login_url='admin_login')
def delete_room(request, room_id):
    user_profile = request.user.profile
    room = get_object_or_404(Room, id=room_id)
    
    # Check permission
    if user_profile.role == 'admin' and room.admin_type != user_profile.admin_type:
        return HttpResponseForbidden("Access denied")
    elif user_profile.role == 'student':
        return HttpResponseForbidden("Access denied")
    
    if request.method == 'POST':
        room_name = room.name
        room.delete()
        messages.success(request, f'Room "{room_name}" deleted successfully!')
        return redirect('admin_dashboard')
    
    context = {'room': room}
    return render(request, 'rooms/delete_room.html', context)

@login_required(login_url='student_login')
@require_http_methods(["GET"])
def room_calendar(request, room_id):
    """Display calendar view for a specific room"""
    room = get_object_or_404(Room, id=room_id)
    
    # Get the month and year from query parameters
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    
    # Get all reservations for this room
    reservations = Reservation.objects.filter(
        room=room,
        status__in=['approved', 'pending']
    )
    
    # Create calendar data
    import calendar
    cal = calendar.monthcalendar(year, month)
    
    # Get day names
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Format reservations by date
    reserved_dates = {}
    for reservation in reservations:
        date_str = str(reservation.date)
        if date_str not in reserved_dates:
            reserved_dates[date_str] = []
        reserved_dates[date_str].append({
            'time': f"{reservation.start_time} - {reservation.end_time}",
            'student': reservation.student.username,
            'status': reservation.status,
        })
    
    # Get previous and next month info
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    context = {
        'room': room,
        'calendar': cal,
        'day_names': day_names,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'reserved_dates': reserved_dates,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    
    return render(request, 'rooms/room_calendar.html', context)