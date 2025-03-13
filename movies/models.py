from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _



class Genre(models.Model):
    tmdb_genre_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_genre(cls, tmdb_genre_id, name):
        genre, created = cls.objects.get_or_create(tmdb_genre_id=tmdb_genre_id, defaults={"name": name})
        return genre

class Movie(models.Model):
    tmdb_id = models.IntegerField(primary_key=True)
    tmdb_type = models.CharField(max_length=10,default='movie')
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    poster_url = models.URLField(null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.title

class TVSeries(models.Model):
    tmdb_id = models.IntegerField(primary_key=True)
    tmdb_type = models.CharField(max_length=10,default='tv')
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    poster_url = models.URLField(null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.title

class Review(models.Model):
    movie = models.ForeignKey(Movie, null=True, blank=True, on_delete=models.CASCADE, related_name='reviews')
    tv_series = models.ForeignKey(TVSeries, null=True, blank=True, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movies = models.ManyToManyField(Movie, blank=True)
    tv_series = models.ManyToManyField(TVSeries, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s watchlist"



class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
        if not password:
            raise ValueError(_('The Password field must be set'))


        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return self.email
    
     
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    

