"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application


from core.middlewares import WSAuthenticationCheckMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django_asgi_app = get_asgi_application()

from django.conf import settings
from chats.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # "websocket": AllowedHostsOriginValidator(
    #     AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    # ),
    "websocket": WSAuthenticationCheckMiddleware(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns)))
})