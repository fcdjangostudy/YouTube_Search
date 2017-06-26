from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from ..forms.profile_edit import UserEditForm

__all__ = (
    'profile',
    'profile_edit',
)


def profile(request, user_pk=None):
    page = request.GET.get('page')
    try:
        page = int(page) if int(page) > 1 else 1
    except ValueError:
        page = 1
    except Exception as e:
        page = 1
        print(e)

    if user_pk:
        user = get_object_or_404(User, pk=user_pk)
    else:
        user = request.user  # 자기 자신의 프로필을 보여줌

    posts = user.post_set.order_by('-created_date')[:page * 3]
    post_count = user.post_set.count()
    next_page = page + 1 if post_count > page * 3 else None
    context = {
        'cur_user': user,
        'posts': posts,
        'post_count': post_count,
        'page': page,
        'next_page': next_page,
    }

    if request.method == 'POST':
        request.user.follow_toggle(user)
        redirect('member:profile', user_pk=user.pk)
        context = {
            'cur_user': user,
            'posts': posts,
            'post_count': post_count,
            'page': page,
        }
    return render(request, 'member/profile.html', context)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserEditForm(data=request.POST, instance=request.user, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('member:my_profile')
    else:
        form = UserEditForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'member/useredit.html', context)
