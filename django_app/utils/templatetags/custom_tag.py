from django import template

register = template.Library()


@register.filter
def query_string(q):
    # value에는 query_dict가 온다
    return '?' + ''.join(['&{}={}'.format(k, v) for k, v_list in q.lists() for v in v_list])