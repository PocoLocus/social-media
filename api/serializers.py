from rest_framework import serializers
from core.models import Post


class PostSerializers(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "author", "content", "tags", "likes", "liked_by", "created_at", "updated_at"]