from rest_framework import permissions


class IsAdminUserOrIsAuthenticatedReadOnly(permissions.BasePermission):
    """
    仅管理员用户可进行修改
    其他登录用户仅可查看
    """

    def has_permission(self, request, view):
        # 对所有认证用户允许 GET, HEAD, OPTIONS 请求
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True

        # 仅管理员可进行其他操作
        return request.user.is_staff

