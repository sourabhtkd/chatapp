import enum
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.db.models import Q
from django.forms import model_to_dict
from django.utils import timezone

from accounts.serializers import UserListSerializer
from chats.models import Conversation, Message, ConversationParticipants
from chats.serializers import MessageSerializer


class ChatConsumer(WebsocketConsumer):
    class ACTIONS(enum.Enum):
        CREATE_MESSAGE = 'CREATE_MESSAGE'
        EDIT_MESSAGE = 'EDIT_MESSAGE'
        TYPING_STATUS_ON = 'TYPING_STATUS_ON'
        TYPING_STATUS_OFF = 'TYPING_STATUS_OFF'

    def connect(self):
        self.user = self.scope['user']
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        query_params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        conversation_id = query_params.get("conversation_id")
        if not conversation_id:
            raise Exception()
        conversation = Conversation.objects.filter(id=conversation_id)
        if not conversation:
            raise Exception()
        conversation = conversation.first()
        self.conversation = conversation
        self.group_name = str(conversation.id)
        self.conversation_id = conversation.id
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {"type": "typing.status",
                              "action": self.ACTIONS.TYPING_STATUS_OFF.value
                              })

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        if not action:
            raise Exception('No action is defined')
        if action == self.ACTIONS.CREATE_MESSAGE.value:
            content = text_data_json["data"]['content']
            message = Message.objects.create(
                conversation_id=self.conversation_id,
                sender=self.user,
                content=content,
            )
            recievers = list(ConversationParticipants.objects.filter(
                Q(conversation_id=self.conversation_id),
                ~Q(user=self.user)

            ).values_list('user_id', flat=True))

            message.unread_by.set(recievers)
            message.save()
            message_data = MessageSerializer(message).data
            message_data.pop('conversation')
            async_to_sync(self.channel_layer.group_send)(
                self.group_name, {"type": "create.message",
                                  "message":message_data ,
                                  "action":action
                                  }
            )
        elif action == self.ACTIONS.EDIT_MESSAGE.value:
            data = text_data_json["data"]
            message_id = data.get('message_id')
            content = data.get('content')
            message = Message.objects.filter(id=message_id).first()
            if message is None:
                raise Exception('Invalid message id')
            if self.user != message.sender:
                raise Exception('Unauthorized Access')

            if (timezone.now() - message.created_at).total_seconds() > 300:
                raise Exception('Cannot edit message after 5 mins')
            message.content = content
            message.edited = True
            message.save()
            message_data = MessageSerializer(message).data
            message_data.pop('conversation')

            async_to_sync(self.channel_layer.group_send)(
                self.group_name, {"type": "update.message",
                                  "message": message_data,
                                  "action":action
                                  }
            )
        elif action in [self.ACTIONS.TYPING_STATUS_ON.value,self.ACTIONS.TYPING_STATUS_OFF.value]:
            async_to_sync(self.channel_layer.group_send)(
                self.group_name, {"type": "typing.status",
                                  "action": action
                                  })

    def create_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        user_serializer = UserListSerializer(self.user)
        self.send(text_data=json.dumps({"message": message,
                                        "action": event['action']
                                        }
                                       ))

    def update_message(self, event):
        message = event["message"]
        # Send message to WebSocket
        user_serializer = UserListSerializer(self.user)
        self.send(text_data=json.dumps({"message": message,
                                        "action": event['action']
                                        }
                                       ))

    def typing_status(self, event):
        # Send message to WebSocket
        user_serializer = UserListSerializer(self.user)
        self.send(text_data=json.dumps({"action": event['action'],
                                        "sender": user_serializer.data
                                        }
                                       ))


# upload avatar
# unread message
