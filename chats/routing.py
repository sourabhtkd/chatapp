from django.urls import re_path

from chats import consumers

websocket_urlpatterns = [
    re_path(r"chats/$", consumers.ChatConsumer.as_asgi(),name='chats'),
]