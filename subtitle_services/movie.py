import re

class Movie(object):

    def __init__(self, id, name, **kwargs):
        self.id = id
        self.title = name
        self.title = re.sub("\([^\)]*\)", "", self.title)
        self.title = re.sub("^the", "", self.title, flags=re.IGNORECASE)
        self.title = self.title.strip()
        self.duration = "1h 20min"
    
    def to_dict(self):
        return {
            "title": self.title,
            "duration": self.duration
        }