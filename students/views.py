from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db import OperationalError
from .forms import EditProfileForm

def user_is_student(user):
    try:
        return user.groups.filter(name='Students').exists() or (not user.is_staff and not user.is_superuser)
    except Exception:
        return not user.is_staff and not user.is_superuser

@login_required
def edit_profile(request):
    if not user_is_student(request.user):
        return HttpResponseForbidden("Forbidden")

    # use the related_name defined on the Profile model
    try:
        profile = getattr(request.user, 'student_profile', None)
    except OperationalError:
        messages.error(request, "Database tables missing for the students app. Run: python manage.py makemigrations students && python manage.py migrate")
        # redirect to site root — replace '/' with a valid named route if you have one
        return redirect('/')
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        pw_form = PasswordChangeForm(request.user, request.POST)
        if 'save_profile' in request.POST and form.is_valid():
            form.save()
            return redirect('students:edit_profile')
        if 'change_password' in request.POST and pw_form.is_valid():
            user = pw_form.save()
            update_session_auth_hash(request, user)
            return redirect('students:edit_profile')
    else:
        form = EditProfileForm(instance=profile, user=request.user)
        pw_form = PasswordChangeForm(request.user)

    return render(request, 'students/edit_profile.html', {
        'form': form,
        'pw_form': pw_form,
        'profile': profile,
    })

@login_required
def view_profile(request):
    if not user_is_student(request.user):
        return HttpResponseForbidden("Forbidden")
    try:
        profile = getattr(request.user, 'student_profile', None)
    except OperationalError:
        messages.error(request, "Database tables missing for the students app. Run: python manage.py makemigrations students && python manage.py migrate")
        return redirect('/')
    return render(request, 'students/profile.html', {
        'profile': profile,
        'user': request.user,
    })