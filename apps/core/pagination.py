from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100


class OptionalPagination(StandardResultsSetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        if 'page' not in request.query_params and 'pagenumber' not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)
