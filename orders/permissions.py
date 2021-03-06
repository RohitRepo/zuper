from rest_framework import permissions

class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_customer()

class IsAgent(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_agent()

class IsStaff(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff

class IsCreator(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.is_owner(request.user)

class IsCreatorOrAgent(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
    	if request.user.is_agent:
    		return True

        return obj.is_owner(request.user)

class CanUpdateStatus(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        

        return True

class IsStaffOrCustomerWriteOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True

    	if request.method == 'POST':
            return request.user.is_customer()

class IsCreatorOrStaffOrAssignedTo(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        return obj.is_owner(request.user) or obj.is_assigned(request.user) or request.user.is_staff

class IsAssignedTo(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        return obj.is_assigned(request.user)

