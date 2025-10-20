from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import UserProfile
import random
import string
from django.utils import timezone
from users.models import PasswordResetToken
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm

def student_login(request):
    # If already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.role == 'student':
            return redirect('student_dashboard')
        elif profile.role in ['admin', 'superadmin']:
            return redirect('admin_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Get user by email
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            
            if user is not None:
                profile = user.profile
                if profile.role == 'student':
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('student_dashboard')
                else:
                    messages.error(request, 'This account is not a student account. Please use admin login.')
            else:
                messages.error(request, 'Invalid password. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email. Please register.')
    
    return render(request, 'users/student_login.html')

def student_register(request):
    # If already logged in, redirect to appropriate dashboard
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.role == 'student':
            return redirect('student_dashboard')
        elif profile.role in ['admin', 'superadmin']:
            return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate email domain
        if not email.endswith('@tip.edu.ph'):
            messages.error(request, 'Please use your TIP email address (@tip.edu.ph)')
            return render(request, 'users/student_register.html')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return render(request, 'users/student_register.html')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'This username is already taken.')
            return render(request, 'users/student_register.html')
        
        # Check password match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/student_register.html')
        
        # Check password length
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'users/student_register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Create student profile
            UserProfile.objects.create(
                user=user,
                role='student'
            )
            
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('student_login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'users/student_register.html')
    
    return render(request, 'users/student_register.html')

def admin_login(request):
    # If already logged in as admin/superadmin, redirect to admin dashboard
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile.role in ['admin', 'superadmin']:
                return redirect('admin_dashboard')
            else:
                logout(request)
        except UserProfile.DoesNotExist:
            logout(request)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                profile = user.profile
                if profile.role in ['admin', 'superadmin']:
                    login(request, user)
                    messages.success(request, f'Welcome, {user.username}!')
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'This account is not an admin account. Please use student login.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'This user account is not properly configured. Contact administrator.')
        else:
            # Check if username exists but password is wrong
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Invalid password. Please try again.')
            else:
                messages.error(request, 'No admin account found with this username.')
    
    return render(request, 'users/admin_login.html')

def logout_view(request):
    user_profile = request.user.profile if request.user.is_authenticated else None
    logout(request)
    
    # Redirect based on user role
    if user_profile and user_profile.role in ['admin', 'superadmin']:
        return redirect('admin_login')
    else:
        return redirect('student_login')

@login_required(login_url='student_login')
def student_dashboard(request):
    reservations = request.user.reservations.all()
    
    # Calculate stats
    pending = reservations.filter(status='pending').count()
    approved = reservations.filter(status='approved').count()
    rejected = reservations.filter(status='rejected').count()
    
    # Get notifications (rejected or newly approved)
    notifications = reservations.filter(status__in=['rejected', 'approved']).order_by('-updated_at')[:3]
    
    context = {
        'reservations': reservations,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'notifications': notifications,
    }
    return render(request, 'reservations/student_dashboard.html', context)

def forgot_password(request):
    """Forgot password page - student enters email"""
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.role == 'student':
            return redirect('student_dashboard')
        elif profile.role in ['admin', 'superadmin']:
            return redirect('admin_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            profile = user.profile
            
            if profile.role != 'student':
                messages.error(request, 'This email is not associated with a student account.')
                return render(request, 'users/forgot_password.html')
            
            # Generate 6-digit verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            
            # Delete old tokens for this email
            PasswordResetToken.objects.filter(email=email).delete()
            
            # Create new token
            token = PasswordResetToken.objects.create(
                user=user,
                email=email,
                verification_code=verification_code
            )
            
            # For now, just display the code (simulate email)
            request.session['reset_email'] = email
            request.session['reset_code'] = verification_code
            messages.info(request, f'Verification code sent to {email}. (For demo: {verification_code})')
            
            return redirect('verify_code')
        
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return render(request, 'users/forgot_password.html')
    
    return render(request, 'users/forgot_password.html')

def verify_code(request):
    """Verify the code sent to email"""
    if request.method == 'POST':
        entered_code = request.POST.get('verification_code')
        reset_email = request.session.get('reset_email')
        
        try:
            token = PasswordResetToken.objects.get(email=reset_email, verification_code=entered_code)
            
            if not token.is_valid():
                messages.error(request, 'Verification code has expired. Please try again.')
                return redirect('forgot_password')
            
            # Code is valid, proceed to reset password
            request.session['reset_user_id'] = token.user.id
            token.delete()  # Delete used token
            return redirect('reset_password')
        
        except PasswordResetToken.DoesNotExist:
            messages.error(request, 'Invalid verification code.')
            return render(request, 'users/verify_code.html')
    
    reset_email = request.session.get('reset_email')
    if not reset_email:
        return redirect('forgot_password')
    
    context = {'reset_email': reset_email}
    return render(request, 'users/verify_code.html', context)

def reset_password(request):
    """Reset password after verification"""
    reset_user_id = request.session.get('reset_user_id')
    
    if not reset_user_id:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('student_login')
    
    try:
        user = User.objects.get(id=reset_user_id)
    except User.DoesNotExist:
        return redirect('student_login')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate passwords
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'users/reset_password.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/reset_password.html')
        
        # Update password
        user.set_password(password)
        user.save()
        
        # Clear session
        if 'reset_email' in request.session:
            del request.session['reset_email']
        if 'reset_code' in request.session:
            del request.session['reset_code']
        if 'reset_user_id' in request.session:
            del request.session['reset_user_id']
        
        messages.success(request, 'Password reset successful! Please log in with your new password.')
        return redirect('student_login')
    
    context = {'email': user.email}
    return render(request, 'users/reset_password.html', context)

@login_required
def edit_profile(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, "Access denied: Students only.")
        return redirect('dashboard')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.student)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('edit_profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.student)

    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'students/edit_profile.html', context)