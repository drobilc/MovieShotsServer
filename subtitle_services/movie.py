class Movie(object):

    def __init__(self, id, title, **kwargs): 
        self.id = id
        self.title = title

        # Set multiple attributes to empty string
        default_empty_fields = ["duration", "year", "cover"]
        for key in default_empty_fields:
            setattr(self, key, "")

        # Iterate over received arguments and override default argument values
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def update_duration(self, runtime):
        hours = runtime // 60
        minutes = runtime % 60
        self.duration = "{}h {}min".format(hours, minutes)

    def update_information(self, response):
        # When additional movie information is downloaded (that is before the
        # game is constructed), save it
        self.additional_information = response

        if response['overview']:
            self.overview = response['overview']

        if response['runtime']:
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