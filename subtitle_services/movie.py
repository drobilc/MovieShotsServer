from datetime import datetime

class Movie(object):

    def __init__(self, id, title, **kwargs): 
        self.id = id
        self.title = title

        # Set multiple attributes to empty string
        default_empty_fields = [('duration', ''), ('year', 0), ('cover', '')]
        for key, value in default_empty_fields:
            setattr(self, key, value)

        # Iterate over received arguments and override default argument values
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def update_duration(self, runtime):
        hours = runtime // 60
        minutes = runtime % 60
        self.duration = "{}h {}min".format(hours, minutes)
    
    def update_cover_photo(self, subtitle_service, poster_path, poster_size=0):
        self.cover = subtitle_service.construct_cover_url(poster_path, poster_size)
    
    def update_year(self, release_date):
        self.year = 0
        try:
            # The release date from TMDB is in format YYYY-MM-DD, only extract
            # year. The release date can also be empty so wrap it in try-except
            # block to ensure this doesn't crash.
            full_release_date = datetime.strptime(release_date, '%Y-%m-%d')
            self.year = full_release_date.year
        except Exception as e:
            pass

    def update_information(self, subtitle_service, response, poster_size=0):
        # When additional movie information is downloaded (that is before the
        # game is constructed), save it
        self.additional_information = response

        if 'title' in response and response['title'] is not None:
            self.title = response['title']

        if 'overview' in response and response['overview'] is not None:
            self.overview = response['overview']
        
        if 'release_date' in response and response['release_date'] is not None:
            self.update_year(response['release_date'])
        
        if 'poster_path' in response and response['poster_path'] is not None:
            self.update_cover_photo(subtitle_service, response['poster_path'], poster_size)

        if 'runtime' in response and response['runtime'] is not None:
            self.update_duration(response['runtime'])
        
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "overview": self.overview if hasattr(self, 'overview') else '',
            "year": self.year,
            "duration": self.duration,
            "cover": self.cover
        }
    
    def __str__(self):
        return '<Movie title="{}">'.format(self.title)
    
    def __repr__(self):
        return '<Movie title="{}">'.format(self.title)