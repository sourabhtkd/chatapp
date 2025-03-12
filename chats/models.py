from django.contrib.auth import get_user_model
from django.db import models

from chats.enums import ConversationType
from common.models import BaseUUIDModel

User = get_user_model()


class Conversation(BaseUUIDModel):
    name = models.CharField(max_length=255)
    conversation_type = models.CharField(choices=ConversationType.choices, max_length=1)
    participants = models.ManyToManyField(User, through='ConversationParticipants', related_name='conversations')
    last_message_excerpt = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} -> {self.conversation_type}"


# to track joined at
class ConversationParticipants(BaseUUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)


# Create your models here.
class Message(BaseUUIDModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='message_sender', on_delete=models.CASCADE)
    content = models.TextField()
    unread_by = models.ManyToManyField(User, related_name='unread_messages')
    deleted_by = models.ManyToManyField(User, related_name='deleted_messages')
    edited = models.BooleanField(default=False)
