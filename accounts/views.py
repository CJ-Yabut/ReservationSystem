from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfilePhotoForm

@login_required
def profile_photo_view(request):
    # adjust if your profile relation is different (e.g., request.user.userprofile)
    profile = getattr(request.user, 'student_profile', None)
    if profile is None:
        # if image field is on User model, use the user object
        profile = request.user

    if request.method == 'POST':
        form = ProfilePhotoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('students:profile')  # replace 'profile' with your "My profile" url name
    else:
        form = ProfilePhotoForm(instance=profile)

    return render(request, 'accounts/profile_photo.html', {'form': form})
