from django import template

# 自定义过滤器
register = template.Library()
import logging

logger = logging.getLogger('tasks')
from asset.models import AssetProject


@register.filter
def result(text):
    for i, j in enumerate(text):
        try:
            a = j['data']
            out = a.replace('\n', '<br>')
            j['data'] = out
        except Exception as e:
            pass
            try:
                j = "{0}".format(text['exc_message'].replace('\n', '<br>'))
                return j
            except Exception as e:
                pass
    return text


@register.filter
def traceback(text):
    try:
        a = text.replace('\n', '<br>')
    except Exception as e:
        logger.error(e)
        a = text
    return a


@register.filter
def objectasset(text):
    try:
        a = AssetProject.objects.get(id=text).projects
    except Exception as e:
        logger.error(e)
        a = text
    return a
