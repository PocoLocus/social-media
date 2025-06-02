from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q

from .forms import CustomSignupForm, LoginForm, PostForm, CommentForm
from .models import Post, Tag, CustomUser


def welcome(request):
    return render(request, "core/welcome.html")

def signup(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            messages.success(request, "Your account has been successfully created!")
            return redirect("home")
        else:
            messages.error(request, "Error creating the account. Please check the form.")
    else:
        form = CustomSignupForm()
    return render(request, "registration/signup.html", context={
        "form": form
    })

# It could also be done with the use of auth built-in AuthenticationForm.
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            credential = form.cleaned_data["credential"]
            password = form.cleaned_data["password"]
            try:
                user = CustomUser.objects.get(Q(username=credential) | Q(email=credential))
            except:
                messages.error(request, "Wrong username or email.")
            else:
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "Your have successfully logged in!")
                    return redirect("home")
                else:
                    messages.error(request, "Wrong password.")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", context={
        "form": form
    })

class CustomPasswordResetView(PasswordResetView, SuccessMessageMixin):
    template_name = "registration/password-reset.html"
    email_template_name = "registration/password-reset-email.html"
    subject_template_name = "registration/password-reset-subject.txt"
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy("welcome")

class HomeView(LoginRequiredMixin, View):
    login_url = "login"

    def get(self, request):
        posts = Post.objects.all().order_by("-updated_at")
        tags = Tag.objects.all()
        form = CommentForm()
        return render(request, "core/home.html", context={
            "posts": posts,
            "form": form,
            "tags": tags
        })

    def post(self, request):
        posts = Post.objects.all().order_by("-updated_at")
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = request.POST.get("post_id")
            new_comment = form.save(commit=False)
            new_comment.commenter = request.user
            new_comment.post = get_object_or_404(Post, id=post_id)
            new_comment.save()
            messages.success(request, "Your comment has been successfully submitted!")
            return redirect("home")
        return render(request, "core/home.html", context={
            "posts": posts,
            "form": form
        })

class CheckUserProfileView(HomeView):
    def get(self, request, username):
        posts = Post.objects.filter(author__username=username).order_by("-updated_at")
        tags = Tag.objects.all()
        form = CommentForm()
        return render(request, "core/home.html", context={
            "posts": posts,
            "form": form,
            "tags": tags,
            "page_title": f"{username}'s profile"
        })

class SortByTagView(HomeView):
    def get(self, request, tag_name):
        tag = get_object_or_404(Tag, name=tag_name)
        posts = Post.objects.filter(tags=tag).order_by("-updated_at")
        tags = Tag.objects.all()
        form = CommentForm()
        return render(request, "core/home.html", context={
            "posts": posts,
            "form": form,
            "tags": tags,
            "page_title": f"#{tag_name}"
        })

@login_required(login_url="login")
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            form.save_m2m() # Save the tags (ManyToManyField)
            messages.success(request, "Your post has been successfully submitted!")
            return redirect("home")
    else:
        form = PostForm()
    return render(request, "core/create-post.html", context={
        "form": form
    })

@login_required(login_url="login")
def edit_post(request, post_id):
    post_to_edit = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post_to_edit)
        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.author = request.user
            updated_post.save()
            form.save_m2m()  # Save the tags (ManyToManyField)
            messages.success(request, "Your post has been successfully updated!")
            return redirect("home")
    else:
        # Prepopulate the form
        form = PostForm(instance=post_to_edit)
    return render(request, "core/edit-post.html", context={
        "form": form
    })

@login_required(login_url="login")
def delete_post(request, post_id):
    post_to_delete = get_object_or_404(Post, id=post_id)
    post_to_delete.delete()
    return redirect("home")


