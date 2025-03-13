from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView 
from .views import (
    RegisterView, LogoutView, MovieListView, MovieDetailView, 
    ReviewCreateView, WatchlistListView, UserDetailView,
    WatchlistAddView, WatchlistRemoveView, ReviewListView, 
    GenreCreateView, GenreDetailView, test_reviews_endpoint, TVSeriesDetailView, TVSeriesListView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'), 
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('movies/', MovieListView.as_view(), name='movie_list'),
    path('movies/<int:tmdb_id>/', MovieDetailView.as_view(), name='movie_detail'),
    path('tv/', TVSeriesListView.as_view(), name='tv_list'),
    path('tv/<int:tmdb_id>/', TVSeriesDetailView.as_view(), name='tv_detail'),  
    path('reviews/', ReviewCreateView.as_view(), name='add_review'),  
    path('watchlist/', WatchlistListView.as_view(), name='user_watchlist'),  
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('watchlist/add/', WatchlistAddView.as_view(), name='watchlist_add'),
    path('watchlist/remove/', WatchlistRemoveView.as_view(), name='watchlist_remove'),
    path('reviews/<int:tmdb_id>/<str:media_type>/', ReviewListView.as_view(), name='review-list'),
    path('test-reviews/<int:tmdb_id>/', test_reviews_endpoint, name='test-reviews'),  
    path('genres/', GenreCreateView.as_view(), name='genre-create'),  
    path('genres/<int:tmdb_genre_id>/', GenreDetailView.as_view(), name='genre-detail'), 
]
