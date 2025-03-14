from django.urls import path
# from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path("", views.WelcomeView.as_view(), name="welcome"),
    # path("accounts/login", auth_views.LoginView.as_view(), name="login"), ## It is included through "path("accounts/", include("django.contrib.auth.urls"))"
    # path("accounts/logout", auth_views.LogoutView.as_view(), name="logout"), ## It is included through "path("accounts/", include("django.contrib.auth.urls"))"
    path("accounts/signup", views.signup, name="signup"),
    path("home", views.HomeView.as_view(), name="home"),
    path("create-post", views.create_post, name="create_post"),
    path("user/<slug:username>", views.CheckUserProfileView.as_view(), name="check_user_profile"),
    path("tag/<str:tag_name>", views.SortByTagView.as_view(), name="sort_by_tag"),
    path("edit-post/<int:post_id>", views.edit_post, name="edit_post"),
    path("delete-post/<int:post_id>", views.delete_post, name="delete_post"),
]