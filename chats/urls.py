from django.urls import path
from chats import views
from rest_framework import routers

from chats.views import ConversationModelViewSet
from chats.ws_doc_view import WebSocketDocsView

app_name = 'chats'
simple_router = routers.SimpleRouter(trailing_slash=False)
simple_router.register('conversations', ConversationModelViewSet, 'conversations')

urlpatterns = simple_router.urls
urlpatterns += [
    path("ws/docs/chats/", WebSocketDocsView.as_view(), name="ws-docs-chat"),
]
