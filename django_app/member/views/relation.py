from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from member.models import User


@require_POST
@login_required
def follow_toggle(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    request.user.follow_toggle(user)
    return redirect('member:my_profile', user_pk=user_pk)


@require_POST
@login_required
def block_toggle(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    request.user.block_toggle(user)
    return redirect('member:my_profile', user_pk=user_pk)
