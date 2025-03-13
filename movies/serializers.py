from rest_framework import serializers
from .models import Movie, Review, Watchlist, CustomUser, Genre, TVSeries
from django.contrib.auth import get_user_model, authenticate


User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField() 

    class Meta:
        model = Review
        fields = ['id', 'movie', 'tv_series', 'content', 'created_at', 'user'] 

    def get_user(self, obj):
        return obj.user.username 

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)

    def validate_content(self, value):
        if not value:
            raise serializers.ValidationError("Content cannot be empty.")
        return value

class WatchlistActionSerializer(serializers.Serializer):
    tmdb_id = serializers.IntegerField()


class WatchlistDetailSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Watchlist
        fields = ['id', 'items']

    def get_items(self, obj):
        movies = [{
            'tmdb_id': movie.tmdb_id,
            'title': movie.title,
            'poster_url': movie.poster_url,
            'media_type': movie.tmdb_type,
        } for movie in obj.movies.all()]

        tv_series = [{
            'tmdb_id': tv.tmdb_id,
            'title': tv.title,
            'poster_url': tv.poster_url,
            'media_type': tv.tmdb_type,
        } for tv in obj.tv_series.all()]

        return movies + tv_series


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        data['user'] = user
        return data
    
   


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['tmdb_genre_id', 'name'] 


class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Movie
        fields = ['tmdb_id', 'title', 'description', 'release_date', 'poster_url', 'vote_average', 'tmdb_type', 'genres']


    def create(self, validated_data):
        
         genres_data = validated_data.pop('genres', [])
        
         movie = Movie.objects.create(**validated_data)
       
         for genre_data in genres_data:
            genre = Genre.get_or_create_genre(
                tmdb_genre_id=genre_data['tmdb_genre_id'],
                name=genre_data['name']
            )
            movie.genres.add(genre)
         return movie


    def update(self, instance, validated_data):
        genres_data = validated_data.pop('genres', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

       
        instance.genres.clear()
        for genre_data in genres_data:
            genre = Genre.get_or_create_genre(
                tmdb_genre_id=genre_data['tmdb_genre_id'],
                name=genre_data['name']
            )
            instance.genres.add(genre)

        return instance


class TVSeriesSerializer(serializers.ModelSerializer):
    genres = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = TVSeries
        fields = ['tmdb_id', 'title', 'description', 'release_date', 'poster_url', 'vote_average', 'tmdb_type', 'genres']


    def create(self, validated_data):
        
         genres_data = validated_data.pop('genres', [])
        
         tv_series = TVSeries.objects.create(**validated_data)
       
         for genre_data in genres_data:
            genre = Genre.get_or_create_genre(
                tmdb_genre_id=genre_data['tmdb_genre_id'],
                name=genre_data['name']
            )
            tv_series.genres.add(genre)
            return tv_series


    def update(self, instance, validated_data):
        genres_data = validated_data.pop('genres', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

       
        instance.genres.clear()
        for genre_data in genres_data:
            genre = Genre.get_or_create_genre(
                tmdb_genre_id=genre_data['tmdb_genre_id'],
                name=genre_data['name']
            )
            instance.genres.add(genre)

        return instance