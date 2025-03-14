from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, Comment, CustomUser


class SignupForm(UserCreationForm):
    # Email is not required by default in Django
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "image", "password1", "password2"]

    # Check that the given email is unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "tags"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
