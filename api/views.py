from django.http import JsonResponse
from django.conf import settings
from django.core.files.base import ContentFile

from .models import *
from .exceptions import *

from .subtitle_service import SubtitleService
from .generator import DrinkingGame

from io import BytesIO
import srt
import json

# Global subtitle service for downloading and parsing subtitles that is
# available to all views in this file
subtitle_service = SubtitleService(
    tmdb_api_key=settings.TMDB_API_KEY,
    opensubtitles_username=settings.OPENSUBTITLES_USERNAME,
    opensubtitles_password=settings.OPENSUBTITLES_PASSWORD
)

def generate_game(request):
    # When generating a game, a few parameters must first be read
    #   * movie - the name of the movie to generate game for
    #   * movie_id - the id of the movie the user wants to generate the game for
    #   * intoxication - number of shots the users wants to drink
    #   * players - number of players that the game must be generated for
    movie_title = request.GET.get('movie', default=None)
    intoxication_level = int(request.GET.get('intoxication', default=8))
    number_of_players = int(request.GET.get('players', default=4))

    movie_id = request.GET.get('movie_id', default=None)

    # The movie_id argument is only present when user clicks on a suggestion
    # card inside suggestions adapter in Android app. If both, movie_id and
    # movie arguments are present, the movie_id parameter is used beucase it
    # uniquely describes our movie.
    if movie_id is not None:
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            # There was an error loading movie from local database, get movie
            # from TMDB service and save it to local database
            movie = subtitle_service.get_movie(movie_id)
            movie.save()
    else:
        # If movie_id is None and movie_title isn't, then we must perform two
        # requests to TMDB API. First, we use movie_title to get a list of
        # suggestions and then use the most probable suggestion from this list.
        if movie_title is not None:
            suggestions, _ = subtitle_service.get_suggestions(movie_title)

            if suggestions is None or len(suggestions) <= 0:
                raise MovieNotFoundException(movie_title)
            
            movie = subtitle_service.get_movie(suggestions[0].id)
            movie.save()
        else:
            raise InvalidParametersException('movie or movie_id')

    # After movie information has either been downloaded or read from local
    # database, find its subtitles. The subtitles might have already been
    # downloaded. In this case, only the game needs to be generated.
    if movie.subtitles_file:
        subtitle_file_path = movie.subtitles_file.url
        with open(subtitle_file_path, 'r', encoding='utf-8') as subtitle_file:
            subtitle_generator = srt.parse(subtitle_file.read())
    else:
        subtitle_file_content, subtitle_generator = subtitle_service.get_subtitles(movie)

        file_io = BytesIO(subtitle_file_content)
        movie.subtitles_file.save(
            "{}.srt".format(movie.id),
            content = ContentFile(file_io.getvalue())
        )
    
    # Here, subtitle generator has been created, now we can create game
    game = DrinkingGame(
        movie,
        subtitle_generator,
        number_of_players,
        intoxication_level
    )
    game_json = game.to_dict(subtitle_service)

    # If there was an exception during game generation process, Django will exit
    # here. Once game has been successfully generated, we can save it to local
    # database. The game id will be generated automatically by Django.
    game_database = Game(
        number_of_players=game.number_of_players,
        intoxication_level=game.intoxication_level,
        number_of_bonus_words=game.number_of_bonus_words,
        game_data=json.dumps(game_json),
        movie=movie,
        created_by=request.api_user
    )
    game_database.save()

    game_json['id'] = str(game_database.id)
    return JsonResponse(game_json)

def rate_game(request):
    game_id = request.GET.get('game', default=None)
    rating = request.GET.get('rating', default=None)

    if not game_id:
        raise InvalidParametersException('game')

    if not rating:
        raise InvalidParametersException('rating')

    try:
        game = Game.objects.get(id=int(game_id))
        rating_database = Rating(user=request.api_user, game=game, rating=rating)
        rating_database.save()
    except Exception:
        pass

    return JsonResponse({
        'game': game_id,
        'rating': rating
    })

def suggestions(request):
    keywords = request.GET.get('keywords', None)

    if not keywords:
        raise InvalidParametersException('keywords')

    suggestions, response = subtitle_service.get_suggestions(keywords)
    return JsonResponse([suggestion.to_dict(subtitle_service, 0) for suggestion in suggestions], safe=False)

def trending_movies(request):
    page = request.GET.get('page', default=1)
    return JsonResponse(subtitle_service.get_popular(page), safe=False)

def game_details(request, game_id):
    try:
        game = Game.objects.get(pk=game_id)
        game_json = json.loads(game.game_data)
        game_json['id'] = str(game.id)
        print(game_json)
        return JsonResponse(game_json, safe=False)
    except Game.DoesNotExist:
        raise GameNotFoundException(game_id)
    return 

def asset_links(request):
    return JsonResponse(settings.DIGITAL_ASSET_LINKS_FILE_CONTENT, safe=False)