import rest_framework.exceptions
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from chats.enums import ConversationType
from chats.models import Conversation, Message
from chats.serializers import ConversationCreateSerializer, ConversationListSerializer, MessageSerializer, \
    ParticipantAddSerializer
from rest_framework import mixins

User = get_user_model()
# Create your views here.


@extend_schema_view(
    list=extend_schema(summary="List all Conversations"),
    # retrieve=extend_schema(summary="Retrieve a chat"),
    create=extend_schema(summary="Create a new conversation",description="""
    Creates Conversation and being used for both one to one and Group Chat,
    Before starting any message it is expected to create conversation object.
    - For one to one chat, if pair of participants existed before, same conversation objects will be returned,
      else new conversation object will be created.
    - For Group Conversation expecting name explicitly, at least one participant be there and at most
    10 participant can be there in a group
    
    """),
    messages=extend_schema(summary="List messages of conversation"),
    add_participants_to_group=extend_schema(summary="Add participants to an existing conversation/group",
                                            request=ParticipantAddSerializer,
                                            responses={200:{'message': 'success'}}),
)
class ConversationModelViewSet(mixins.ListModelMixin, CreateModelMixin, GenericViewSet):

    def get_queryset(self):
        qs = Conversation.objects.filter(
            participants__in=[self.request.user]
        )
        return qs

    def get_serializer_class(self):

        if self.action == 'create':
            return ConversationCreateSerializer
        else:
            return ConversationListSerializer

    @action(methods=['GET'], url_path='messages', detail=True)
    def messages(self, request, *args, **kwargs):
        conversation_id = kwargs.get('pk')
        if Conversation.objects.filter(id=conversation_id).exists() is False:
            raise rest_framework.exceptions.NotFound()
        messages = Message.objects.filter(conversation_id=conversation_id).order_by('-created_at')
        paginator = self.paginator
        paginated_messages = paginator.paginate_queryset(messages, request)

        Message.unread_by.through.objects.filter(user=request.user,
                                                 message__in=paginated_messages).delete()
        message_serializer = MessageSerializer(paginated_messages, many=True)
        # print(dir(paginator.page)
        response_data = {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": message_serializer.data
        }

        return Response(response_data)

    @action(methods=["POST"], url_path='add-participants', detail=True)
    def add_participants_to_group(self, request, *args, **kwargs):
        conversation_id = kwargs.get('pk')
        conversation = Conversation.objects.filter(id=conversation_id).first()
        if conversation is None:
            raise rest_framework.exceptions.NotFound()

        serializer = ParticipantAddSerializer(data=request.data)
        serializer.context['conversation'] = conversation
        serializer.context['current_user'] = request.user

        serializer.is_valid(raise_exception=True)
        conversation.participants.add(serializer.validated_data.get('new_participant'))
        # conversation.last_message_excerpt = f"{request.user.first_name} {request.user.last_name} added {}"
        return Response({'message': 'success'})
