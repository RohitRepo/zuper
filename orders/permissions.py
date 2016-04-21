from rest_framework import permissions

class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_customer()

class IsAgent(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_agent()

class IsCreator(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.customer.id

class IsCreatorOrAgent(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
    	if request.user.is_agent:
    		return True

        return request.user.id == obj.customer.id

class CanUpdateStatus(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_agent():
        	return True
        elif request.user.is_customer():
        	return request.data.get('status') == 'CN'

        return False

class IsCustomerOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
    	if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_customer()