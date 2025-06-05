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
from django.http import JsonResponse

from .forms import CustomSignupForm, LoginForm, PostForm, CommentForm
from .models import Post, Tag, CustomUser, Comment


def welcome(request):
    return render(request, "core/welcome.html")

def signup(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            messages.success(request, "Your account has been successfully created!")
            return redirect("chitchat")
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
                    return redirect("chitchat")
                else:
                    messages.error(request, "Wrong password.")
    else:
        form = LoginForm()
    return render(request, "registration/login.html", context={
        "form": form
    })

def change_username(request):
    if request.method == "POST":
        new_username = request.POST.get("new_username", "")
        if not new_username:
            messages.error(request, "Username cannot be empty.")
            return render(request, "registration/change-username.html")
        if new_username == request.user.username:
            messages.error(request, "You are already using this username.")
            return render(request, "registration/change-username.html")
        if CustomUser.objects.filter(username=new_username).exists():
            messages.error(request, "This name is already taken.")
            return render(request, "registration/change-username.html")
        request.user.username = new_username
        request.user.save()
        messages.success(request, "Your username has been successfully changed!")
        return redirect("chitchat")
    return render(request, "registration/change-username.html")

class CustomPasswordResetView(PasswordResetView, SuccessMessageMixin):
    template_name = "registration/password-reset.html"
    email_template_name = "registration/password-reset-email.html"
    subject_template_name = "registration/password-reset-subject.txt"
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy("welcome")

class ChitChatView(LoginRequiredMixin, View):
    login_url = "login"

    def get_base_context(self):
        return {
            "tags": Tag.objects.all(),
            "comments": Comment.objects.all().order_by("-created_at")[:3],
            "form": CommentForm()
        }

    def get_filtered_posts(self, request, base_queryset):
        q_user = request.GET.get("searched_user", "")
        q_post = request.GET.get("searched_post", "")
        return base_queryset.filter(author__username__icontains=q_user).filter(content__icontains=q_post).order_by("-created_at")

    def get(self, request):
        base_queryset = Post.objects.all()
        posts = self.get_filtered_posts(request, base_queryset)
        context = self.get_base_context()
        context.update({
            "posts": posts,
            "page_title": "ChitChat",
            "type": "main"
        })
        return render(request, "core/chitchat.html", context=context)

    def post(self, request):
        posts = Post.objects.all().order_by("-created_at")
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = request.POST.get("post_id")
            new_comment = form.save(commit=False)
            new_comment.commenter = request.user
            new_comment.post = get_object_or_404(Post, id=post_id)
            new_comment.save()
            messages.success(request, "Your comment has been successfully submitted!")
            return redirect("check_post", post_id)
        context = self.get_base_context()
        context.update({
            "posts": posts,
            "form": form
        })
        return render(request, "core/chitchat.html", context=context)

class CheckUserProfileView(ChitChatView):
    def get(self, request, username):
        base_queryset = Post.objects.filter(author__username=username)
        posts = self.get_filtered_posts(request, base_queryset)
        context = self.get_base_context()
        context.update({
            "posts": posts,
            "page_title": f"{username}'s profile",
            "type": "profile"
        })
        return render(request, "core/chitchat.html", context=context)

class SortByTagView(ChitChatView):
    def get(self, request, tag_name):
        tag = get_object_or_404(Tag, name=tag_name)
        base_queryset = Post.objects.filter(tags=tag)
        posts = self.get_filtered_posts(request, base_queryset)
        context = self.get_base_context()
        context.update({
            "posts": posts,
            "page_title": f"#{tag_name}",
            "type": "main"
        })
        return render(request, "core/chitchat.html", context=context)

class CheckPost(ChitChatView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        context = self.get_base_context()
        context.update({
            "posts": [post],
            "page_title": f"check post: '{post.content[:15]}...'",
            "type": "specific"
        })
        return render(request, "core/chitchat.html", context=context)

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
            return redirect("chitchat")
    else:
        form = PostForm()
    return render(request, "core/create-or-edit-post.html", context={
        "form": form,
        "type": "create"
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
            return redirect("chitchat")
    else:
        # Prepopulate the form
        form = PostForm(instance=post_to_edit)
    return render(request, "core/create-or-edit-post.html", context={
        "form": form
    })

@login_required(login_url="login")
def delete_post(request, post_id):
    post_to_delete = get_object_or_404(Post, id=post_id)
    post_to_delete.delete()
    return redirect("chitchat")

@login_required(login_url="login")
def like_post(request, post_id):
    if request.method == "POST":
        post_to_like = get_object_or_404(Post, id=post_id)
        liked = False
        if request.user not in post_to_like.liked_by.all():
            post_to_like.likes += 1
            post_to_like.liked_by.add(request.user)
            liked = True
        else:
            post_to_like.likes -= 1
            post_to_like.liked_by.remove(request.user)
        post_to_like.save()
        return JsonResponse({
            "success": True,
            "liked": liked,
            "likes": post_to_like.likes
        })

    return JsonResponse({"success": False}, status=400)



