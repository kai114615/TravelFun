from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    自定義權限：
    - 允許所有人讀取
    - 只允許作者修改或刪除
    """
    def has_object_permission(self, request, view, obj):
        # 讀取權限允許任何請求
        if request.method in permissions.SAFE_METHODS:
            return True

        # 寫入權限只允許文章/評論的作者
        return obj.author == request.user

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自定義權限：
    - 允許所有人讀取
    - 只允許管理員修改或刪除
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff 