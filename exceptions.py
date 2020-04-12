class ApiException(Exception):
    
    def __init__(self, code, message):
        self.code = code
        self.message = message
    
    def to_dict(self):
        return {
            "error": True,
            "code": self.code,
            "message": self.message
        }

class InvalidParametersException(ApiException):
    def __init__(self, parameter_name):
        super().__init__(1, "Parameter {} required but not provided".format(parameter_name))

class MovieNotFoundException(ApiException):
    def __init__(self, movie_title):
        super().__init__(5, "Movie {} not found".format(movie_title))

class SubtitlesNotFoundException(ApiException):
    def __init__(self, movie_title):
        super().__init__(6, "Subtitles for movie {} not found".format(movie_title))

class GameGenerationException(ApiException):
    def __init__(self, reason=""):
        super().__init__(7, "The drinking game could not be generated. {}".format(reason))