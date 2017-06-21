from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_POST

from ..decorators import comment_owner
from ..forms.comment import CommentForm
from ..models import Post, Comment

__all__ = (
    'comment_create',
    'comment_modify',
    'comment_delete',
    'post_anyway',
)


@require_POST
@login_required
def comment_create(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)
    next = request.GET.get('next')
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    else:
        messages.error(request, form.errors)

    if next:
        return redirect(next)
    return redirect('post:post_detail', post_pk=post.pk)


@comment_owner
@login_required
def comment_modify(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    next = request.GET.get('next')
    if request.method == 'POST':
        form = CommentForm(data=request.POST, instance=comment)
        form.save()
        if next:
            return redirect(next)
        return request('post:post_derail', post_pk=comment_pk)
    else:
        form = CommentForm(instance=comment)
    context = {
        'form': form,
    }
    return render(request, 'post/comment_modify.html', context)


def comment_delete(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    post = comment.post
    comment.delete()
    return redirect('post:post_detail', post_pk=post.pk)


def post_anyway(request):
    return redirect('post:post_list')
