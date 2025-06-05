from django.urls import path

from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("signup", views.signup, name="signup"),
    path("login", views.login_view , name="login"), # Could be done through built-in LoginView of auth app
    path("logout", auth_views.LogoutView.as_view(next_page="welcome"), name="logout"),

    path("change-username", views.change_username, name="change_username"),
    path("password-reset", views.CustomPasswordResetView.as_view(), name="password_reset"),
    path("password-reset-confirm/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(template_name="registration/password-reset-confirm.html"), name="password_reset_confirm"),
    path("password-reset-complete", auth_views.PasswordResetCompleteView.as_view(template_name="registration/password-reset-complete.html"), name="password_reset_complete"),

    path("", views.welcome, name="welcome"),
    path("chitchat", views.ChitChatView.as_view(), name="chitchat"),
    path("post/<int:post_id>", views.CheckPost.as_view(), name="check_post"),
    path("user/<slug:username>", views.CheckUserProfileView.as_view(), name="check_user_profile"),
    path("tag/<str:tag_name>", views.SortByTagView.as_view(), name="sort_by_tag"),

    path("create-post", views.create_post, name="create_post"),
    path("edit-post/<int:post_id>", views.edit_post, name="edit_post"),
    path("delete-post/<int:post_id>", views.delete_post, name="delete_post"),
    path("like-post/<int:post_id>", views.like_post, name="like_post")
]