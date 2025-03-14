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

# --- FBV alternative --- #
# def welcome(request):
#     return render(request, "core/welcome.html")


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

# --- CBV alternative (more complicated, doesn't work) --- #
# class SignupView(SuccessMessageMixin, CreateView):
#     template_name = "registration/signup.html"
#     form_class = SignupForm
#     success_url = reverse_lazy("home")
#     success_message = "Your account has been successfully created!"
#
#     def form_valid(self, form):
#         self.object = form.save()
#         login(self.request, self.object)
#         return super().form_valid(form)
#
#     def form_invalid(self, form):
#         messages.error(self.request, "Error creating the account. Please check the form.")
#         return super().form_invalid(form)


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

# --- CBV alternative (without Comments) --- #
# class HomeView(LoginRequiredMixin, ListView):
#     login_url = "login"
#     template_name = "core/home.html"
#     model = Post
#     context_object_name = "all_posts"
#     ordering = ["-updated_at"]

# --- FBV alternative (without Comments) --- #
# @login_required(login_url="login")
# def home(request):
#     all_posts = Post.objects.all().order_by("-updated_at")
#     return render(request, "core/home.html", context={
#         "all_posts": all_posts
#     })


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

# --- FBV alternative --- #
# @login_required(login_url="login")
# def check_user_profile(request, username):
#     user_to_check = get_object_or_404(User, username=username)
#     return render(request, "core/check-user-profile.html", context={
#         "user_to_check": user_to_check
#     })


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

# --- CBV alternative (more complicated) --- #
# class CreatePostView(LoginRequiredMixin, CreateView):
#     template_name = "core/create-post.html"
#     form_class = PostForm
#     success_url = reverse_lazy("home")
#
#     def form_valid(self, form):
#         new_post = form.save(commit=False)
#         new_post.author = self.request.user
#         new_post.save()
#         form.save_m2m() # Save the tags (ManyToManyField)
#         messages.success(self.request, "Your post has been successfully submitted!")
#         return super().form_valid(form)
#
#     def form_invalid(self, form):
#         messages.error(self.request, "Error creating the post. Please check the form.")
#         return super().form_invalid(form)


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


