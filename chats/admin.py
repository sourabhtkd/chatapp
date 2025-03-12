from django.contrib import admin
from chats import models as chat_models
from chats.models import Message

# Register your models here.
admin.site.register(chat_models.Conversation)
admin.site.register(chat_models.ConversationParticipants)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", 'conversation', 'sender', 'content']
    ordering = ('-created_at',)


@admin.register(Message.unread_by.through)
class MessageThroughAdmin(admin.ModelAdmin):
    list_display = ['user', 'message']
