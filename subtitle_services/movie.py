class Movie(object):

    def __init__(self, id, title, **kwargs):
        self.id = id
        self.title = title
        self.duration = ""
        self.year = ""
        self.cover = ""

        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        return {
            "title": self.title,
            "year": self.year,
            "duration": self.duration,
            "cover": self.cover
        }
    
    def __str__(self):
        return '<Movie title="{}">'.format(self.title)
    
    def __repr__(self):
        return '<Movie title="{}">'.format(self.title)