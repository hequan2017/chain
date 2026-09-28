"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chain.settings")
django.setup()

# channels 4：ASGI 入口直接复用 chain/routing.py 中定义的 application
from chain.routing import application  # noqa: E402
