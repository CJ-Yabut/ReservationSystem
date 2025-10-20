from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from .models import Profile

class EditProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, label="Username")
    first_name = forms.CharField(max_length=30, required=False, label="First name")
    last_name = forms.CharField(max_length=150, required=False, label="Last name")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = Profile
        fields = ('avatar',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.exclude(pk=self.user.pk).filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise ValidationError("This email is already used.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            username = self.cleaned_data.get('username')
            first_name = self.cleaned_data.get('first_name')
            last_name = self.cleaned_data.get('last_name')
            email = self.cleaned_data.get('email')

            changed = False
            if username and self.user.username != username:
                self.user.username = username
                changed = True
            if first_name is not None and self.user.first_name != first_name:
                self.user.first_name = first_name
                changed = True
            if last_name is not None and self.user.last_name != last_name:
                self.user.last_name = last_name
                changed = True
            if email and self.user.email != email:
                self.user.email = email
                changed = True

            if changed and commit:
                self.user.save()

        if commit:
            profile.user = self.user
            profile.save()
        return profile