import re
from pprint import pprint

import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models import Q
from django.shortcuts import render, redirect

from ..forms import PostForm
from ..models import Video

__all__ = (
    'youtube_create_and_search',
    'video_post_create',
)


# [1] 검색결과를 DB에 저장하고, 해당내용을 템플릿에서 보여주기!
# 1. 유튜브 영상을 저장할 class Video(models.Model)생성
# 2. 검색결과의 videoId를 Video의 youtube_id필드에 저장
#       해당필드는 unique해야 함
# 3. 검색결과에서 videoId가 Video의 youtube_id와 일치하는 영상이 이미 있을경우에는 pass,
#    없을경우 새 Video객체를 만들어 DB에 저장
# 4. 이후 검색결과가 아닌 자체 DB에서 QuerySet을 만들어 필터링한 결과를 템플릿에서 표시

# [2] 위 과제로 완성된 검색결과에서 '포스팅하기'버튼을 구현, Post가 YouTube영상을 포함하도록 함
#    검색결과에서 '포스팅하기'버튼을 누르면, 해당 Video와 연결된 Post를 생성
#    post_list에서 Video와 연결된 Post는 영상을 보여주도록 함

def youtube_create_and_search(request):
    # 기존의 데이터 리스트를 확보합니다.
    videos_in_db = Video.objects.all()
    id_set = [i.video_id for i in videos_in_db]

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
        result = response.json()

        for item in result['items']:
                if item['id']['videoId'] in id_set:
                    break
                else:
                    # 새로운 비디오 객체를 생성하는 구간
                    url_thumbnail = item['snippet']['thumbnails']['high']['url']
                    p = re.compile(r'.*\.([^?]+)')
                    file_ext = re.search(p, url_thumbnail).group(1)
                    file_name = '{}.{}'.format(
                        item['id']['videoId'],
                        file_ext,
                    )
                    temp_file = NamedTemporaryFile()
                    response = requests.get(url_thumbnail)
                    temp_file.write(response.content)
                    video = Video.objects.create(
                        video_id=item['id']['videoId'],
                        title=item['snippet']['title'],
                        description=item['snippet']['description'],
                        created_date=item['snippet']['publishedAt'].split('T')[0]
                    )
                    video.thumbnail.save(file_name, File(temp_file))

        video_list = Video.objects.filter(Q(title__contains=q) | Q(description__contains=q))
        context = {
            'videos': video_list,
        }
    return render(request, 'post/youtube_search.html', context)


def video_post_create(request, video_pk):
    if request.method == 'POST':
        form = PostForm(data=request.POST)
        if form.is_valid():
            post = form.save(author=request.user)
            post.video_id = video_pk
            post.save()
            return redirect('post:post_detail', post_pk=post.pk)
    else:
        form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'post/post_create.html', context)
# def youtube_search(request, ):
#     url_api_search = 'https://www.googleapis.com/youtube/v3/search'
#     q = request.GET.get('q')
#     context = {}
#     if q:
#         url_api_search_params = {
#             'part': 'snippet',
#             'key': 'AIzaSyDS5bkCHVpQKunVKCNheUKV3MDHGK3-LYc',
#             'q': q,
#             'maxResults': '10',
#             'type': 'video',
#         }
#         response = requests.get(url_api_search, params=url_api_search_params)
#         context = {
#             'response': response.json()
#         }
#         pprint(response.json())
#     return render(request, 'post/youtube_search.html', context)
