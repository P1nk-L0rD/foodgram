from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)


class CustomPagination(LimitOffsetPagination, PageNumberPagination):
    page_size_query_param = 'limit'
