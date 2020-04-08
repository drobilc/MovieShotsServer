class ApiException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

class MovieNotFoundException(ApiException):
    def __init__(self, movie_title):
        super().__init__(1, "Movie {} not found".format(movie_title))

class SubtitlesNotFoundException(ApiException):
    def __init__(self, movie_title):
        super().__init__(2, "Subtitles for movie {} not found".format(movie_title))

class GameGenerationException(ApiException):
    def __init__(self):
        super().__init__(3, "The drinking game could not be generated")