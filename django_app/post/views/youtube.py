from pprint import pprint

import requests
from django.shortcuts import render

__all__ = (
    'youtube_search',
)


def youtube_search(request,):

    url_api_search = 'https://www.googleapis.com/youtube/v3/search'
    q = request.GET.get('q')
    context = {}
    if q:
        url_api_search_params = {
            'part': 'snippet',
            'key': 'AIzaSyDS5bkCHVpQKunVKCNheUKV3MDHGK3-LYc',
            'q': q,
            'maxResults': '10',
            'type': 'video',
        }
        response = requests.get(url_api_search, params=url_api_search_params)
        context = {
            'response': response.json()
        }
        pprint(response.json())
    return render(request, 'post/youtube_search.html', context)
