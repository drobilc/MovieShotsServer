from django.http import JsonResponse
from django.conf import settings

from .subtitle_service import SubtitleService

# Global subtitle service for downloading and parsing subtitles that is
# available to all views in this file
subtitle_service = SubtitleService(
    tmdb_api_key=settings.TMDB_API_KEY,
    opensubtitles_username=settings.OPENSUBTITLES_USERNAME,
    opensubtitles_password=settings.OPENSUBTITLES_PASSWORD
)

def generate_game(request):
    return JsonResponse({})

def rate_game(request):
    return JsonResponse({})

def suggestions(request):
    return JsonResponse([])

def trending_movies(request):
    page = request.GET.get('page', default=1)
    return JsonResponse(subtitle_service.get_popular(page), safe=False)