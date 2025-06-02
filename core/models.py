from django.db import models

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

    def __str__(self):
        return f"{self.content} ({self.commenter})"
