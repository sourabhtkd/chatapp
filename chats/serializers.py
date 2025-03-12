import rest_framework.exceptions
from django.db.models import Count
from rest_framework import serializers
from chats.models import *
from accounts.serializers import UserListSerializer


class ConversationListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    unread_count = serializers.SerializerMethodField(method_name='get_unread_count')

    class Meta:
        model = Conversation
        fields = ('id', 'name', 'conversation_type', 'last_message_excerpt', 'participants',
                  'unread_count', 'created_at', 'updated_at')

    def get_unread_count(self, instance):
        unread_count = Message.objects.filter(conversation_id=instance.id,
                                              unread_by=self.context['request'].user
                                              ).count()
        return unread_count


class ConversationCreateSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True  # Indicates this is a Many-to-Many field
    )
    name = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    last_message_excerpt = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = Conversation
        fields = ('id', 'name', 'conversation_type', 'participants', 'last_message_excerpt', 'created_at', 'updated_at')

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        conversation_type = validated_data.get('conversation_type')
        participants = validated_data.get('participants')

        if not participants:
            raise serializers.ValidationError({'participants': 'At least one participant is required'})

        if conversation_type == ConversationType.OneToOne.value:
            if len(participants) > 1:
                raise serializers.ValidationError({'participants': 'Can send message to only one, '
                                                                   'for multiple recipient use groups'})
        else:
            name = attrs['name']
            if not name:
                raise serializers.ValidationError({'name': 'Name is required to create group'})
            if len(participants) > 9:
                raise serializers.ValidationError({'participants': 'Group cannot have more than 10 people'})

        return attrs

    def create(self, validated_data):
        conversation_type = validated_data.get('conversation_type')
        participants = validated_data.pop('participants')
        request = self.context.get('request')
        if conversation_type == ConversationType.OneToOne:
            conversation_ids = ConversationParticipants.objects.values(
                'conversation'
            ).annotate(
                num_participants=Count('user')
            ).filter(
                num_participants=2
            ).values_list('conversation', flat=True)

            conversation = Conversation.objects.filter(
                id__in=conversation_ids,
                participants__in=[participants[0], request.user]
            ).first()
            if conversation:
                return conversation
            else:
                conversation = Conversation.objects.create(
                    name=f"{participants[0].first_name}, {request.user.first_name}",
                    **validated_data
                )
                conversation.participants.set([request.user, participants[0]])
                return conversation
        else:
            conversation = Conversation.objects.create(
                **validated_data
            )
            participants.append(request.user)
            conversation.participants.set(participants)
            conversation.last_message_excerpt = f"{request.user.first_name} {request.user.last_name} created this group"
            conversation.save()
            return conversation


class MessageSerializer(serializers.ModelSerializer):
    sender = UserListSerializer()

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'content', 'edited')


class ParticipantAddSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        email = attrs.get('email')
        conversation = self.context.get('conversation')
        current_user = self.context.get('current_user')
        if not email:
            raise rest_framework.exceptions.ValidationError({'email': "user_email is required"})

        if conversation.conversation_type != ConversationType.Group:
            raise rest_framework.exceptions.ValidationError('Cannot add people in one to one conversation')

        new_participant = User.objects.filter(email=email).first()
        if not new_participant:
            raise rest_framework.exceptions.ValidationError('User with this email does not exist')
        if conversation.participants.filter(
                id=new_participant.id
        ).exists():
            raise rest_framework.exceptions.ValidationError('User with this email already exists in this group')

        validated_data['new_participant'] = new_participant
        return validated_data
