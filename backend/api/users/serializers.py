from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.users.fields import Base64ImageField
from users.constants import MAX_USERNAME_LEN
from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    '''Сериализатор для модели User'''

    username = serializers.CharField(
        max_length=MAX_USERNAME_LEN,
    )

    avatar = Base64ImageField(
        required=False,
        allow_null=True,
    )

    is_subscribed = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'avatar', 'is_subscribed',
        )

    def validate(self, attrs):
        if len(attrs) == 0:
            raise serializers.ValidationError('Нет данных.')
        return super().validate(attrs)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')

        return (
            request and request.user.is_authenticated
            and Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        )
