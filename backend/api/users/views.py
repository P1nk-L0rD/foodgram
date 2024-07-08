from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from users.models import Subscription

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет для пользователей."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        """Доработать"""
        if self.action == 'list':
            return UserSerializer
        return UserSerializer

    # def get_permissions(self):
    #     if self.action.startswith('me'):
    #         return (permissions.IsAuthenticated(),)
    #     return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        if self.action == 'me':
            kwargs = {'id': request.user.pk}
            self.action = 'retrieve'

        return super().retrieve(request, *args, **kwargs)

    @action(methods=['PUT'], url_path='avatar', detail=True)
    def set_avatar(self, request, id):
        avatar = request.data.get('avatar')
        User.objects.filter(pk=request.user.pk).update(
            avatar=avatar
        )

        return Response({"avatar": avatar})

    @action(
        methods=['PUT'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='avatar',
    )
    def set_avatar2(self, request, id):
        user = self.request.user
        serialiser = UserSerializer(user)

        if request.method == "PUT":
            serialiser = UserSerializer(
                user, data=request.data, partial=True,
            )
            serialiser.is_valid(raise_exception=True)
            serialiser.save()

            user = User.objects.get(pk=user.pk)
            serialiser = UserSerializer(user)
            return Response({"avatar": user.avatar}, status=status.HTTP_200_OK)
        return Response(serialiser.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='subscribe',
    )
    def subscribe(self, request, id):
        user = self.request.user
        to_sub = get_object_or_404(User, pk=id)
        if user == to_sub:
            return Response(
                {"message": "Нельзя подписаться на самогос себя!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == "POST":
            Subscription.objects.create(
                subscriber=user, author=to_sub,
            )
            return Response(status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            Subscription.objects.filter(
                subscriber=user, author=to_sub,
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='subscriptions',
    )
    def subscriptions(self, request):
        ...
