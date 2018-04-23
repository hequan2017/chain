from django import template
# 自定义过滤器
register = template.Library()
import json
import logging
logger = logging.getLogger('tasks')


@register.filter
def result(text):
    for i, j in enumerate(text):
        try:
            a = j['data']
            out = a.replace('\n','<br>')
            j['data'] = out
        except Exception as e:
            logger.error(e)
            j="{0}".format(text['exc_message'].replace('\n','<br>'))
            return j
    return text


@register.filter
def traceback(text):
    try:
        a = text.replace('\n', '<br>')
    except Exception as e:
        a = text
    return a
