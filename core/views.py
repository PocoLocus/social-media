from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignupForm, PostForm, CommentForm
from .models import Post, Tag
from django.contrib.auth.models import User


class WelcomeView(TemplateView):
    template_name = "core/welcome.html"

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            messages.success(request, "Your account has been successfully created!")
            return redirect("home")
        else:
            messages.error(request, "Error creating the account. Please check the form.")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", context={
        "form": form
    })

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


