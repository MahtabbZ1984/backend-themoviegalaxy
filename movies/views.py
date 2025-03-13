from rest_framework import generics, permissions, status, generics
from .models import Movie, Review, Watchlist, Genre, TVSeries
from .serializers import RegisterSerializer, MovieSerializer, TVSeriesSerializer, ReviewSerializer, WatchlistActionSerializer, WatchlistDetailSerializer, GenreSerializer

from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_reviews_endpoint(request, tmdb_id):
    print(f"Test endpoint hit with tmdb_id: {tmdb_id}")
    return Response({"message": f"Test endpoint working for movie {tmdb_id}"})


User = get_user_model()


def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully."})


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username,  
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=204)
        except Exception as e:
            return Response(status=400)
        

class MovieListView(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class MovieDetailView(generics.RetrieveUpdateAPIView):
    queryset = Movie.objects.filter(tmdb_type='movie')
    serializer_class = MovieSerializer

    def get_object(self):
        tmdb_id = self.kwargs.get('tmdb_id')
        return get_object_or_404(Movie.objects.prefetch_related('genres'), tmdb_id=tmdb_id, tmdb_type='movie')


class TVSeriesListView(generics.ListCreateAPIView):
    
    queryset = TVSeries.objects.all()
    serializer_class = TVSeriesSerializer


class TVSeriesDetailView(generics.RetrieveUpdateAPIView):
    queryset = TVSeries.objects.filter(tmdb_type='tv')
    serializer_class = TVSeriesSerializer

    def get_object(self):
        tmdb_id = self.kwargs.get('tmdb_id')
        return get_object_or_404(TVSeries.objects.prefetch_related('genres'), tmdb_id=tmdb_id, tmdb_type='tv')


class ReviewCreateView(generics.CreateAPIView):
       queryset = Review.objects.all()
       serializer_class = ReviewSerializer
       permission_classes = [permissions.IsAuthenticated]

       def create(self, request, *args, **kwargs):
           print("Request data:", request.data) 
           return super().create(request, *args, **kwargs)

class WatchlistListView(generics.ListAPIView):
    serializer_class = WatchlistDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)


class WatchlistAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        tmdb_id = request.data.get("tmdb_id")
        tmdb_type = request.data.get("tmdb_type")
        watchlist, created = Watchlist.objects.get_or_create(user=request.user)

        if tmdb_type == "tv":
            tv_series = get_object_or_404(TVSeries, tmdb_id=tmdb_id)
            if tv_series not in watchlist.tv_series.all():
                watchlist.tv_series.add(tv_series)
                return Response({"message": "TV series added to watchlist."}, status=status.HTTP_201_CREATED)
            return Response({"message": "TV series is already in watchlist."}, status=status.HTTP_200_OK)
        else:
            movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
            if movie not in watchlist.movies.all():
                watchlist.movies.add(movie)
                return Response({"message": "Movie added to watchlist."}, status=status.HTTP_201_CREATED)
            return Response({"message": "Movie is already in watchlist."}, status=status.HTTP_200_OK)

class WatchlistRemoveView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WatchlistActionSerializer

    def post(self, request, *args, **kwargs):
        serializer = WatchlistActionSerializer(data=request.data)
        if serializer.is_valid():
            tmdb_id = serializer.validated_data['tmdb_id']
            tmdb_type = request.data.get("tmdb_type", "movie")
            watchlist = get_object_or_404(Watchlist, user=request.user)

            if tmdb_type == "tv":
                tv_series = get_object_or_404(TVSeries, tmdb_id=tmdb_id)
                if tv_series in watchlist.tv_series.all():
                    watchlist.tv_series.remove(tv_series)
                    return Response({"message": "TV series removed from watchlist."}, status=status.HTTP_200_OK)
                return Response({"message": "TV series not found in watchlist."}, status=status.HTTP_404_NOT_FOUND)
            else:
                movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
                if movie in watchlist.movies.all():
                    watchlist.movies.remove(movie)
                    return Response({"message": "Movie removed from watchlist."}, status=status.HTTP_200_OK)
                return Response({"message": "Movie not found in watchlist."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
      tmdb_id = self.kwargs['tmdb_id']
      media_type = self.kwargs['media_type']
      if media_type == 'tv':
           reviews = Review.objects.filter(tv_series__tmdb_id=tmdb_id)
      else:
          reviews = Review.objects.filter(movie__tmdb_id=tmdb_id)
      return reviews



class GenreCreateView(generics.CreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def create(self, request, *args, **kwargs):
        tmdb_genre_id = request.data.get('tmdb_genre_id') 

        
        genre, created = Genre.objects.get_or_create(tmdb_genre_id=tmdb_genre_id, defaults={
            'name': request.data.get('name'),
        })

        if created:
            return Response(self.get_serializer(genre).data, status=status.HTTP_201_CREATED)
        return Response(self.get_serializer(genre).data, status=status.HTTP_200_OK)

class GenreDetailView(generics.RetrieveAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    
    def get_object(self):
        tmdb_genre_id = self.kwargs.get('tmdb_genre_id') 
        return get_object_or_404(Genre, tmdb_genre_id=tmdb_genre_id)