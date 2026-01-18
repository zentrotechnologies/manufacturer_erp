from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.core.paginator import InvalidPage
# class CustomPagination(pagination.PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 50
#     page_query_param = 'p'

#     def get_paginated_response(self,data):
#         response = Response({
#             'status':"success",
#             'count':self.page.paginator.count,
#             'next' : self.get_next_link(),
#             'previous' : self.get_previous_link(),
#             'data':data,
#         })
     
#         return response
    
    

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'

    def paginate_queryset(self, queryset, request, view=None):
        # For POST requests, get page number from request.data
        if request.method == 'POST' and hasattr(request, 'data'):
            self.page_size = request.data.get(self.page_size_query_param, self.page_size)
            page_number = request.data.get(self.page_query_param, 1)
        else:
            return super().paginate_queryset(queryset, request, view)
        
        paginator = self.django_paginator_class(queryset, self.page_size)
        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=str(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True

        self.request = request
        return list(self.page)
    
    
class CustomDualPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'

    def get_paginated_response(self,data):
        list1 = data.get('data', [])
        list2 = data.get('suggestions', [])
 
        # You can customize the response to include both lists and pagination metadata
        return Response({
            'count': self.page.paginator.count,  # Total number of items (use the appropriate count)
            'total_pages': self.page.paginator.num_pages,  # Total number of pages
            'current_page': self.page.number,  # Current page number
            'next' : self.get_next_link(),
            'previous' : self.get_previous_link(),
            'data': list1,
            'suggestions': list2,
        })
        
        
        # return response

