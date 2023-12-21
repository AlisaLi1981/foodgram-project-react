from rest_framework.pagination import PageNumberPagination

from recipes.constants import RecipesConstants


class CustomPagination(PageNumberPagination):
    page_size = RecipesConstants.PAGE_SIZE.value
    page_size_query_param = 'limit'
