from .models import User
from django.http import JsonResponse
from django.urls import reverse

from .exceptions import ApiException, NoApiKeyException

class ApiKeyMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(reverse('admin:index')):
            return self.get_response(request)
        
        if request.path.startswith(reverse('asset_links')):
            return self.get_response(request)

        api_key = request.GET.get('api_key', None)

        # If current request does not have an API key, raise an exception that
        # will then be handled by our CustomExceptionMiddleware
        if not api_key:
            return JsonResponse(NoApiKeyException().to_dict())
        else:
            # The API key is present, if there already exists user with api key
            # matching the received one, return it, otherwise create a new user
            try:
                # The user has been found, add it to request
                request.api_user = User.objects.get(api_key=api_key)
            except User.DoesNotExist:
                # The user does not exist, create a new user with received api
                # key and return it
                new_user = User(api_key=api_key)
                new_user.save()
                request.api_user = new_user

        response = self.get_response(request)
        return response

class CustomExceptionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        # This exception middleware will only handle our custom exceptions
        if isinstance(exception, ApiException):
            return JsonResponse(exception.to_dict(), safe=False)