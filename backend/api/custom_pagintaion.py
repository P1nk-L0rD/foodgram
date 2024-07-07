from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination
)


class CustomPagination(LimitOffsetPagination, PageNumberPagination):
    ...
