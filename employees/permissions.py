from rest_framework import permissions

class IsTeacher(permissions.BasePermission):

    def has_permission(self, request, view):
        app_label = view.queryset.model._meta.app_label
        model_name = view.queryset.model._meta.model_name

        if request.method == 'GET':
            return request.user.has_perm(f'can_read_{model_name}')
        elif request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.has_perm(f'can_write_{model_name}')
        elif request.method == 'DELETE':
            return request.user.has_perm(f'can_delete_{model_name}')

        # Default to denying access
        return False

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        app_label = view.queryset.model._meta.app_label
        model_name = view.queryset.model._meta.model_name

        if request.method == 'GET':
            return request.user.has_perm(f'can_read_{model_name}')

        # Default to denying access
        return False