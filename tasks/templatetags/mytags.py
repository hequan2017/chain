from django import template
# 自定义过滤器
register = template.Library()
import json


@register.filter
def result(text):
    for i, j in enumerate(text):
        a = j['data']
        out = "  ".join(a.split())
        j['data'] = out

    return json.dumps(text)
