import json
import logging
from django.db import transaction
from django.http import HttpRequest, HttpResponseNotFound, JsonResponse, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .constants import BASE_URL
from .models import ShortURL
from .utils import get_available_short_url


@csrf_exempt
def create_short_url(request: HttpRequest) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        long_url: str = data.get('url')

        if not long_url:
            return JsonResponse({'error': 'No URL provided'}, status=HttpResponseServerError.status_code)
        
        with transaction.atomic():
            short_url: str = get_available_short_url()

            if not short_url:
                return JsonResponse({'error': 'No more available short URLs'}, status=HttpResponseServerError.status_code)
            
            obj = ShortURL(long_url=long_url, short_url=short_url)
            obj.save()

        return JsonResponse({'short_url': f'{BASE_URL}{short_url}'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)        
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=HttpResponseServerError.status_code)

def redirect_url(request: HttpRequest, short_url: str) -> JsonResponse:
    try:
        obj: ShortURL = ShortURL.objects.get(short_url=short_url)
        obj.hits += 1
        obj.save()
        return redirect(obj.long_url)
    except ShortURL.DoesNotExist:
        return JsonResponse({'error': 'Short URL does not exist'}, status=HttpResponseNotFound.status_code)