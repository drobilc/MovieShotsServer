from django.db import models
from datetime import datetime
import json

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
    release_date = models.DateField(blank=True, null=True)
    cover = models.TextField(blank=True, null=True)

    # Each movie also has a subtitle file from which games are generated. The
    # srt file is saved on disk and has encoding "utf-8"
    subtitles_file = models.FileField(upload_to='subtitles/', blank=True, null=True)
    
    # In order not to overload TMDB movie API, with each movie, we also save
    # (cache) additional movie information that is currently not needed but
    # might be in the future.
    additional_data = models.TextField(blank=True, null=True)
    
    def update_release_date(self, release_date):
        try:
            # The release date from TMDB is in format YYYY-MM-DD, only extract
            # year. The release date can also be empty so wrap it in try-except
            # block to ensure this doesn't crash.
            self.release_date = datetime.strptime(release_date, '%Y-%m-%d')
        except Exception as e:
            pass

    def update_information(self, response):
        # When additional movie information is downloaded (that is before the
        # game is constructed), save it
        self.additional_data = json.dumps(response)

        if 'title' in response and response['title'] is not None:
            self.title = response['title']

        if 'overview' in response and response['overview'] is not None:
            self.overview = response['overview']
        
        if 'release_date' in response and response['release_date'] is not None:
            self.update_release_date(response['release_date'])
        
        if 'poster_path' in response and response['poster_path'] is not None:
            self.cover = response['poster_path']

        if 'runtime' in response and response['runtime'] is not None:
            self.duration = response['runtime']
    
    def year(self):
        if self.release_date is None:
            return 0
        return self.release_date.year
    
    def duration_string(self):
        if self.duration is None:
            return ''
        hours = self.duration // 60
        minutes = self.duration % 60
        return '{}h {}min'.format(hours, minutes)
        
    def to_dict(self, subtitle_service, quality=0):
        return {
            "id": str(self.id),
            "title": self.title,
            "overview": self.overview if self.overview is not None else '',
            "year": self.year(),
            "duration": self.duration_string(),
            "cover": subtitle_service.construct_cover_url(self.cover, quality) if self.cover is not None else ''
        }

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