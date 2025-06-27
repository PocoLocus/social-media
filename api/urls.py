from django.urls import path

from . import views


urlpatterns = [
    path("posts", views.PostListCreate.as_view(), name="posts"),
    path("posts/<int:pk>/", views.PostRetrieveUpdateDestroy.as_view(), name="check_post"),
    path("users", views.UserList.as_view(), name="users"),
    path("movies", views.MovieList.as_view(), name="movies"),
    path("movies/<int:movie_id>/", views.MovieDetail.as_view(), name="movie_detail"),
]