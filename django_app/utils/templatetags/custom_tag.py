from django import template

register = template.Library()


@register.filter  # 이게 필터라는 것을 알려주는 역할
def query_string(q):
    # q에는 query_dict가 온다
    return '?' + ''.join(['&{}={}'.format(k, v) for k, v_list in q.lists() for v in v_list])
