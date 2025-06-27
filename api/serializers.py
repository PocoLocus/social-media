from rest_framework import serializers
from core.models import CustomUser, Post, Movie


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ["password"]

class PostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "author", "content", "tags", "likes", "liked_by", "created_at", "updated_at"]

class MovieListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "release_date"]

class MovieDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"
        read_only_fields = ["vote_average", "added_by", "added_at"]
