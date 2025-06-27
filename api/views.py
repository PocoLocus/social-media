from django.http import Http404
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.models import CustomUser, Post, Movie
from .serializers import UserSerializers, PostSerializers, MovieListSerializers, MovieDetailSerializers


class UserList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializers

class PostListCreate(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializers

    def delete(self, request, *args, **kwargs):
        Post.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializers
    lookup_field = "pk"

# Choose this way only for educational purpose. Could be done easier with generics views.
class MovieList(APIView):
    def get(self, request):
        movies = Movie.objects.all()
        serializer = MovieListSerializers(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MovieDetail(APIView):
    def get_object(self, movie_id):
        try:
            return Movie.objects.get(id=movie_id)
        except:
            raise Http404

    def get(self, request, movie_id):
        movie = self.get_object(movie_id)
        serializer = MovieDetailSerializers(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, movie_id):
        movie = self.get_object(movie_id)
        serializer = MovieDetailSerializers(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, movie_id):
        movie = self.get_object(movie_id)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
