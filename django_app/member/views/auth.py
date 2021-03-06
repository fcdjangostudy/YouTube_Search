import re
from pprint import pprint

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import \
    login as django_login, \
    logout as django_logout, get_user_model
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from django.shortcuts import render, redirect

from ..forms import LoginForm, SignupForm

__all__ = (
    'login',
    'logout',
    'signup',
    'facebook_login',
)

User = get_user_model()


def login(request):
    # member/login.html 생성
    #   username, password, button이 있는 HTML생성
    #   POST요청이 올 경우 좌측 코드를 기반으로 로그인 완료 후 post_list로 이동
    #   실패할경우 HttpResponse로 'Login invalid!'띄워주기

    # member/urls.py생성
    #   /member/login/으로 접근시 이 view로 오도록 설정
    #   config/urls.py에 member/urls.py를 include
    #       member/urls.py에 app_name설정으로 namespace지정

    # POST요청이 왔을 경우
    if request.method == 'POST':
        ### Form클래스 미사용시
        # 요청받은 POST데이터에서 username, password키가 가진 값들을
        # username, password변수에 할당 (문자열)
        # username = request.POST['username']
        # password = request.POST['password']

        # authenticate함수를 사용해서 User객체를 얻어 user에 할당
        # 인증에 실패할 경우 user변수에는 None이 할당됨
        # user = authenticate(
        #     request,
        #     username=username,
        #     password=password
        # )
        # user변수가 None이 아닐 경우 (정상적으로 인증되어 User객체를 얻은 경우)
        # if user is not None:
        #     # Django의 session을 이용해 이번 request와 user객체를 사용해 로그인 처리
        #     # 이후의 request/response에서는 사용자가 인증된 상태로 통신이 이루어진다
        #     django_login(request, user)
        #     # 로그인 완료후에는 post_list뷰로 리다이렉트 처리
        #     return redirect('post:post_list')

        ### Form클래스 사용시
        #   Bound form생성
        form = LoginForm(data=request.POST)
        # Bound form의 유효성을 검증
        #   https://docs.djangoproject.com/en/1.11/topics/forms/#building-a-form-in-django
        if form.is_valid():
            user = form.cleaned_data['user']
            django_login(request, user)
            # 일반적인 경우에는 post_list로 이동하지만,
            # GET parameter의 next속성값이 있을 경우 해당 URL로 이동
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect('post:post_list')
    # GET요청이 왔을 경우 (단순 로그인 Form보여주기)
    else:
        # 만약 이미 로그인 된 상태일 경우에는
        # post_list로 redirect
        # 아닐경우 login.html을 render해서 리턴
        if request.user.is_authenticated:
            return redirect('post:post_list')
        # LoginForm인스턴스를 생성해서 context에 넘김
        form = LoginForm()
    context = {
        'form': form,
    }
    # render시 context에는 LoginForm클래스형 form객체가 포함됨
    return render(request, 'member/login.html', context)


def logout(request):
    # 로그아웃되면 post_list로 redirect
    django_logout(request)
    return redirect('post:post_list')


def signup(request):
    # url은 /member/signup/$
    # member/signup.html을 사용
    #   username, password1, password2를 받아 회원가입
    #   이미 유저가 존재하는지 검사
    #   password1, 2가 일치하는지 검사
    #   각각의 경우를 검사해서 틀릴경우 오류메시지 리턴
    #   가입에 성공시 로그인시키고 post_list로 리다이렉트
    if request.method == 'POST':
        ### Form을 사용하지 않는 경우
        # username, password1, password2에 POST로 전달받은 데이터를 할당
        # username = request.POST['username']
        # password1 = request.POST['password1']
        # password2 = request.POST['password2']
        # # username에 해당하는 User가 있는지 검사
        # if User.objects.filter(username=username).exists():
        #     # 이미 존재하는 username일경우
        #     return HttpResponse('Username is already exist')
        # # password1과 password2가 같은지 검사
        # elif password1 != password2:
        #     # 다를경우
        #     return HttpResponse('Password and Password check are not equal')
        # # 위의 두 경우가 아닌 경우 유저를 생성
        # user = User.objects.create_user(
        #     username=username,
        #     password=password1
        # )

        ### Form을 사용한 경우
        form = SignupForm(data=request.POST)
        if form.is_valid():
            user = form.create_user()
            django_login(request, user)
            return redirect('post:post_list')
    else:
        form = SignupForm()
    context = {
        'form': form,
    }
    return render(request, 'member/signup.html', context)


def facebook_login(request):
    code = request.GET.get('code')
    app_access_token = '{}|{}'.format(
        settings.FACEBOOK_APP_ID,
        settings.FACEBOOK_SECRET_CODE,
    )

    class GetAccessTokenException(Exception):
        def __init__(self, *args, **kwargs):
            error_dict = args[0]['data']['error']
            self.code = error_dict['code']
            self.message = error_dict['message']
            self.is_valid = error_dict['is_valid']
            self.scopes = error_dict['scopes']

    class DebugTokenExceptions(Exception):
        def __init__(self, *args, **kwargs):
            error_dict = args[0]['data']['error']
            self.code = error_dict['code']
            self.message = error_dict['message']

    def debug_token(token):
        url_debug_token = 'https://graph.facebook.com/debug_token'
        url_debug_token_params = {
            'input_token': token,
            'access_token': app_access_token,
        }

        response = requests.get(url_debug_token, url_debug_token_params)
        result = response.json()
        if 'error' in result['data']:
            raise DebugTokenExceptions(result)
        else:
            pprint(result)
            return result

    def add_mesage_and_redirect_referer():
        error_message_for_user = 'Facebook login error'
        messages.error(request, error_message_for_user)
        return redirect(request.META['HTTP_REFERER'])

    def get_access_token(code):
        """
        code를 받아 엑세스토큰 교환 url에 요청 이후 해당 엑세스토큰을 반환
        오류 발생시 오류메세지 리턴
        :param code:
        :return:
        """
        redirect_uri = '{}://{}{}'.format(
            request.scheme,
            request.META['HTTP_HOST'],
            request.path,
        )
        url_access_token = 'https://graph.facebook.com/v2.9/oauth/access_token'

        # 엑세스 토큰 받아오기
        url_access_token_params = {
            'client_id': settings.FACEBOOK_APP_ID,
            'redirect_uri': redirect_uri,
            'client_secret': settings.FACEBOOK_SECRET_CODE,
            'code': code,
        }
        resoponse = requests.get(url_access_token, params=url_access_token_params)
        result = resoponse.json()
        pprint(result)

        # error_message = 'Facebook login error\n type: {}\n message: {}'.format(
        #     result['error']['type'],
        #     result['error']['message'],
        # )

        if 'access_token' in result:
            return result['access_token']
        elif 'error' in result:
            raise GetAccessTokenException(result)
        else:
            raise Exception('Unknown error')

    def get_user_info(user_id, token):
        url_user_info = 'https://graph.facebook.com/v2.9/{user_id}'.format(user_id=user_id)
        url_user_info_parms = {
            'access_token': token,
            'fields': ','.join([
                'id',
                'name',
                'first_name',
                'last_name',
                'picture.type(large)',
                'gender',
                'email',
            ])
        }
        response = requests.get(url_user_info, params=url_user_info_parms)
        result = response.json()
        return result

    if not code:
        return add_mesage_and_redirect_referer()

    try:
        access_token = get_access_token(code)
        debug_result = debug_token(access_token)

        user_info = get_user_info(user_id=debug_result['data']['user_id'], token=access_token)

        pprint(user_info)

        user = User.objects.get_or_create_facebook_user(user_info)

        django_login(request, user)
        return redirect(request.META['HTTP_REFERER'])

    except GetAccessTokenException as e:
        pprint(e)
        return add_mesage_and_redirect_referer()
    except DebugTokenExceptions as e:
        pprint(e)
        return add_mesage_and_redirect_referer()
