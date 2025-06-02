from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment, CustomUser


class CustomSignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "image", "password1", "password2"]

    # Check that the given email is unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class LoginForm(forms.Form):
    credential = forms.CharField(label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput())

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "tags"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
