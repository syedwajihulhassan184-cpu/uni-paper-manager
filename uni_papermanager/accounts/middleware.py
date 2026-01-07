from django.shortcuts import redirect 
from django.urls import reverse


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.path.startswith('/admin-panel/') and request.user.user_type != 'admin':
                return redirect('access_denied')
            
            if request.path.startswith('/student-portal/') and request.user.user_type != 'student':
                return redirect('access_denied')
            
        response = self.get_response(request)
        return response
    