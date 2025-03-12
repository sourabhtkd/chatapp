from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')

    def create(self, validated_data):
        email = validated_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': "User already exists"})

        validated_data['username'] = validated_data.get('email')

        user = User(**validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')
