# -*- coding:utf-8 -*-
from rest_framework.permissions import BasePermission, SAFE_METHODS
from menu.models import Menu
from users.models import User, Ops_Group
import re


class MenuPermissionRequired(BasePermission):

    def get_groups_required(self, path):
        pk_path = re.sub(r'(\d+)', '<pk>', path)
        final_results = []
        for menu_obj in Menu.objects.filter(urls__isnull=False):
            url_info = menu_obj.urls
            for url in url_info.split(","):
                if ".*" in url:
                    if re.findall(url, pk_path):
                        final_results.append(menu_obj)
                else:
                    if pk_path == url:
                        final_results.append(menu_obj)
        # results_with_partial_match = Menu.objects.filter(urls__contains=pk_path)
        # final_results = [result for result in results_with_partial_match if pk_path in result.urls.split(",")]
        authed_groups = Ops_Group.objects.filter(menu_permissions__in=final_results).distinct()
        return authed_groups

    def has_permission(self, request, view):
        """
        Override this method to customize the way permissions are checked.
        """
        user = request.user
        if not user.is_authenticated or not user.is_active:
            return False
        if request.method in SAFE_METHODS:
            return True
        if user.is_superuser:
            return True
        authed_groups = self.get_groups_required(request.path)
        authed_users = User.objects.filter(groups__in=authed_groups).distinct()
        if user in authed_users:
            return True
        return False
