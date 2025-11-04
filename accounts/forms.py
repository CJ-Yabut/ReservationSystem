from django import forms
from students.models import Profile

class ProfilePhotoForm(forms.ModelForm):
    avatar = forms.ImageField(label="Upload Photo")

    class Meta:
        model = Profile   # or use get_user_model() if image is on User
        fields = ['avatar']  # replace 'avatar' with your image field name
