# -*- coding:utf-8 -*-
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from common.permissions import MenuPermissionRequired



class MenuTreeView(ListAPIView):
    queryset = Menu.objects.filter(parent__isnull=True).order_by("order")
    serializer_class = MenuTreeSerializer
    permission_classes = [IsAuthenticated]


class MenuIndexView(MenuTreeView):

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        result = serializer.data
        # add_custom_workflow(result)
        return result


class MenuListCreateView(ListCreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [MenuPermissionRequired]


class MenuOperateView(RetrieveUpdateDestroyAPIView):
    serializer_class = MenuSerializer
    permission_classes = [MenuPermissionRequired]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        return Menu.objects.filter(id=self.kwargs.get("pk"))
