from rest_framework import permissions

class IsAdminOrManager(permissions.BasePermission):
    """
    Позволяет доступ только администраторам (is_staff) или пользователям с ролью 'Manager'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Проверка на суперпользователя или стафф
        if request.user.is_superuser or request.user.is_staff:
            return True
            
        # Проверка на роль 'Manager'
        return request.user.roles.filter(name__iexact='Manager').exists()
