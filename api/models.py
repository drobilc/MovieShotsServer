from django.db import models

class User(models.Model):
    # Users are only identified with an API key that is generated on device as a
    # random UUID. This ensures that each app installation can only vote once
    # per game, though it is possible to clear app data and reset this key.
    api_key = models.CharField(max_length=160)
    ratings = models.ManyToManyField('Game', through='Rating')

class Movie(models.Model):
    # For our purposes, each movie must have an id. In our case, the id will be
    # the TMDB movie id which can then be used to access IMDB movie id and
    # consequently get subtitles from OpenSubtitles database.
    # The only fields that should not be null are the movie id and title.
    id = models.CharField(max_length=160, primary_key=True)
    title = models.CharField(max_length=240)
    overview = models.TextField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    cover = models.TextField(blank=True, null=True)

    # Each movie also has a subtitle file from which games are generated. The
    # srt file is saved on disk and has encoding "utf-8"
    subtitles_file = models.FileField(upload_to='subtitles/', blank=True, null=True)
    
    # In order not to overload TMDB movie API, with each movie, we also save
    # (cache) additional movie information that is currently not needed but
    # might be in the future.
    additional_data = models.TextField(blank=True, null=True)

class Game(models.Model):
    # Game information such as how many players are playing this game and how
    # many shots each one should drink.
    number_of_players = models.IntegerField()
    intoxication_level = models.IntegerField()
    number_of_bonus_words = models.IntegerField()
    
    game_data = models.TextField()
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    ratings = models.ManyToManyField(User, through='Rating')

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    rating = models.FloatField()