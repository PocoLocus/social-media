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
import requests

from .forms import CustomSignupForm, LoginForm, PostForm, CommentForm
from .models import Post, Tag, CustomUser, Comment, Movie, Rating


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
        user_to_check = CustomUser.objects.get(username=username)
        base_queryset = Post.objects.filter(author__username=username)
        posts = self.get_filtered_posts(request, base_queryset)
        context = self.get_base_context()
        context.update({
            "posts": posts,
            "page_title": f"{username}'s profile",
            "type": "profile",
            "user_to_check": user_to_check
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

@login_required(login_url="login")
def movies(request):
    movies = Movie.objects.all().order_by("-added_at")
    for movie in movies:
        rating_obj = movie.ratings.filter(user=request.user).first()
        movie.current_user_rating = rating_obj.rating if rating_obj else None
    if request.method == "POST":
        rating = request.POST.get("rating")
        movie_id = request.POST.get("movie_id")
        current_movie = Movie.objects.get(id=movie_id)
        rating_obj, created = Rating.objects.update_or_create(
            user=request.user,
            movie=current_movie,
            defaults={"rating":rating}
        )
        if created:
            messages.success(request, "Movie successfully rated!")
        else:
            messages.success(request, "You have successfully updated your rating!")
        return redirect('movies')
    return render(request, "core/movies.html", context={
        "movies": movies
    })

@login_required(login_url="login")
def search_movie_online(request):
    query = request.GET.get("searched_movie", "").strip()
    tmdb_page = request.GET.get("tmdb_page", 1)
    available_movies = []
    tmdb_total_pages = 1
    if query:
        url = "https://api.themoviedb.org/3/search/movie"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhYzFiM2E4ODJlM2IzZGI4ZGVmNjQ0NDhiMWRlMzdkNCIsIm5iZiI6MTcyOTU4NjU2MC45NzcsInN1YiI6IjY3MTc2NTgwNmZiMDllMzk0YzAyOWQ4MSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.QNo6zhVT2QxldV-6gQZqjAxUui_cII-wjRnvHczkY3o"
        }
        params = {
            "query": query,
            "include_adult": False,
            "language": "en-US",
            "page": tmdb_page
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            available_movies = data.get("results", [])
            tmdb_total_pages = data.get("total_pages", 1)
            for movie in available_movies:
                movie["movie_exists"] = Movie.objects.filter(title=movie["title"], overview=movie["overview"]).exists()
        except:
            messages.error(request, "Failed to fetch movies. Please try again later.")
            return redirect("search_movie_online")
    return render(request, "core/search-movie-online.html", context={
        "available_movies": available_movies,
        "searched": query,
        "tmdb_page": int(tmdb_page),
        "tmdb_total_pages": tmdb_total_pages
    })

@login_required(login_url="login")
def add_movie(request):
    if request.method == "POST":
        title = request.POST.get("title")
        release_date = request.POST.get("release_date")
        overview = request.POST.get("overview")
        vote_average = request.POST.get("vote_average")
        poster_path = request.POST.get("poster_path")
        rating = request.POST.get("rating")
        new_movie = Movie(
            title=title,
            release_date=release_date,
            overview=overview,
            vote_average=vote_average,
            poster_path=poster_path,
            added_by=request.user
        )
        new_movie.save()
        new_rating = Rating(
            user=request.user,
            movie=new_movie,
            rating=rating
        )
        new_rating.save()
        messages.success(request, "Movie successfully added!")
        return redirect('movies')

