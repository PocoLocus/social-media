from django.db import models
from django.db.models import Avg

from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    image = models.ImageField(upload_to="profile_icons", null=True, blank=True) # In ModelForms blank affects the form validation
    email = models.EmailField(unique=True, blank=False) # email is not unique and is not required by default in Django

    def __str__(self):
        return self.username

    # To display the groups at the admin panel
    def get_groups(self):
        groups = []
        for group in self.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    get_groups.short_description = 'Groups'


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    tags = models.ManyToManyField(Tag)
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(CustomUser)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.content[:20]} ({self.author})"

    # To display the tags at the admin panel
    def get_tags(self):
        return ", ".join([tag.name for tag in self.tags.all()])
    get_tags.short_description = "Tags"


class Comment(models.Model):
    commenter = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content} ({self.commenter})"

class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    overview = models.TextField()
    vote_average = models.FloatField()
    poster_path = models.CharField(max_length=255)
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="movies")
    added_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.release_date})"

    def average_rating(self):
        return self.ratings.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0.0

class Rating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="personal_ratings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    rating = models.FloatField()
    created_at = models.DateField(auto_now_add=True)


