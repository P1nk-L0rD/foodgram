from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.recipes.serializers import (SubscriptionCreateSerializer,
                                     SubscriptionSerializer)
from api.users.serializers import UserSerializer
from users.models import Subscription

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет для пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        if self.action and self.action == 'me':
            if self.request.user.is_anonymous:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            kwargs = {'id': request.user.pk}
            self.action = 'retrieve'

        return super().retrieve(request, *args, **kwargs)

    @action(
        methods=['PUT', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='avatar',
    )
    def manage_avatar(self, request, id):
        """Функция для управления аватаркой."""
        user = self.request.user
        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = UserSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            user = User.objects.get(pk=user.id)
            return Response(
                {"avatar": str(user.avatar)},
                status=status.HTTP_200_OK,
            )

        if request.method == 'DELETE':
            User.objects.filter(pk=user.id).update(avatar=None)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='subscribe',
    )
    def subscribe(self, request, id):
        """Функция для подписки на других пользователей."""
        user = self.request.user
        to_sub = get_object_or_404(User, pk=id)
        if user == to_sub:
            return Response(
                {"errors": "Нельзя подписаться на самого себя!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        exist = Subscription.objects.filter(
            user=user, author=to_sub,
        ).exists()

        if request.method == "POST":
            if exist:
                return Response(
                    {"error": "Вы уже подписаны на этого пользователя!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = SubscriptionCreateSerializer(
                data={'user': user.id, 'author': to_sub.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if not exist:
                return Response(
                    {"errors": "Вы уже отписаны от этого пользователя!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.filter(
                user=user, author=to_sub,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        """Функция для получения списка подписок."""

        queryset = User.objects.filter(author__user=self.request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
