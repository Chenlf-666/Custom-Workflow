# -*- coding:utf-8 -*-
import coreschema
from coreapi import Field

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.serializers import BaseSerializer
from rest_framework.permissions import IsAuthenticated
from .filter import *
from .serializers import *
from .models import *
from common.Constant import CUSTOM_STATE
from common.permissions import MenuPermissionRequired

from users.models import User, Ops_Group


QueryModelList = [User, Ops_Group]


class WorkflowListCreateAPI(ListCreateAPIView):
    queryset = Custom_Workflow.objects.all()
    serializer_class = CustomWorkflowSerializer
    permission_classes = [MenuPermissionRequired]
    filterset_class = CustomWorkflowFilter


class ContentTypeListAPI(ListCreateAPIView):
    serializer_class = ContentTypeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get_queryset(self):
        content_type_list = [ContentType.objects.get_for_model(model).id for model in QueryModelList]
        return ContentType.objects.filter(id__in=content_type_list)


class WorkflowDetailAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = CustomWorkflowSerializer
    permission_classes = [MenuPermissionRequired]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        return Custom_Workflow.objects.filter(id=self.kwargs.get("pk"))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.ticket_set.all():
            return Response(
                data={"message": "已存在关联工单，无法删除"},
                status=status.HTTP_400_BAD_REQUEST
            )
        Menu.objects.filter(name=instance.name).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkflowActiveAPI(ListCreateAPIView):
    serializer_class = CustomWorkflowSerializer
    permission_classes = [MenuPermissionRequired]
    http_method_names = ["post"]

    def get_queryset(self):
        return Custom_Workflow.objects.filter(id=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            return Response(
                data={"message": "该工作流已激活"},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance.is_active = True
        instance.save()
        return Response(data={"message": "Success"}, status=status.HTTP_200_OK)


class FieldListCreateAPI(ListCreateAPIView):
    serializer_class = CustomFieldSerializer
    permission_classes = [MenuPermissionRequired]
    filterset_class = CustomFieldFilter

    def get_queryset(self):
        workflow = Custom_Workflow.objects.get(id=self.kwargs.get("pk"))
        return Custom_Field.objects.filter(workflow=workflow).order_by("order_id", "-update_time")

    def post(self, request, *args, **kwargs):
        instance = Custom_Workflow.objects.get(id=self.kwargs.get("pk"))
        serializer = CustomFieldSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workflow=instance)
        return Response(serializer.data)


class FieldDetailAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = CustomFieldSerializer
    permission_classes = [MenuPermissionRequired]
    http_method_names = ["get", "put", "delete"]

    def get_object(self):
        return Custom_Field.objects.get(id=self.kwargs.get("field_id"))


class FieldRelateUrlAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = BaseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get_object(self):
        return Custom_Field.objects.get(id=self.kwargs.get("field_id"))

    def get(self, request, *args, **kwargs):
        field = self.get_object()
        foreign_type = field.foreign_type
        special_url = field.special_url
        if foreign_type:
            if foreign_type == ContentType.objects.get_for_model(User):
                return Response(data={"url": "/auth/users"})
            elif foreign_type == ContentType.objects.get_for_model(Ops_Group):
                return Response(data={"url": "/auth/groups"})
            else:
                return Response(data={"url": ""})
        if special_url:
            return Response(data={"url": special_url})
        return Response(data={"url": ""})


class NewFieldRelateUrlAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = BaseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get_object(self):
        return Custom_Field.objects.get(id=self.kwargs.get("field_id"))

    def get(self, request, *args, **kwargs):
        field = self.get_object()
        foreign_type = field.foreign_type
        special_url = field.special_url
        if foreign_type:
            if foreign_type == ContentType.objects.get_for_model(User):
                queryset = User.objects.filter(is_active=True)
                serializer = RelateUserSerializer(queryset, many=True)
            elif foreign_type == ContentType.objects.get_for_model(Ops_Group):
                queryset = Ops_Group.objects.all()
                serializer = RelateGroupSerializer(queryset, many=True)
            else:
                return Response(data={"results": []})
            return Response(data={"results": serializer.data})
        if special_url:
            return Response(data={"url": special_url})
        return Response(data={"results": []})


class StatusListCreateAPI(ListCreateAPIView):
    serializer_class = StatusSerializer
    permission_classes = [MenuPermissionRequired]

    def get_queryset(self):
        workflow = Custom_Workflow.objects.get(id=self.kwargs.get("pk"))
        return Custom_State.objects.filter(workflow=workflow).order_by("order_id", "-update_time")

    def post(self, request, *args, **kwargs):
        instance = Custom_Workflow.objects.get(id=self.kwargs.get("pk"))
        serializer = StatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workflow=instance)
        return Response(serializer.data)


class StatusDetailAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = StatusDetailSerializer
    permission_classes = [MenuPermissionRequired]
    http_method_names = ["get", "put", "delete"]

    def get_object(self):
        return Custom_State.objects.get(id=self.kwargs.get("status_id"))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.ticket_set.all():
            return Response(
                data={"message": "已存在处于该状态的工单，无法删除"},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class InitialStatusAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = StatusDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get_queryset(self):
        return Custom_Workflow.objects.filter(id=self.kwargs.get("pk"))

    def get(self, request, *args, **kwargs):
        workflow = self.get_object()
        if workflow.status_list.filter(state_type=CUSTOM_STATE.TYPE.Init):
            instance = workflow.status_list.get(state_type=CUSTOM_STATE.TYPE.Init)
        else:
            return Response(
                data={"message": "未创建初始化自定义状态"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class TransitionListCreateAPI(ListCreateAPIView):
    serializer_class = TransitionSerializer
    permission_classes = [MenuPermissionRequired]

    def get_queryset(self):
        workflow = Custom_Workflow.objects.get(id=self.kwargs.get("pk"))
        return Custom_Transition.objects.filter(workflow=workflow).order_by("-update_time")

    def post(self, request, *args, **kwargs):
        instance = Custom_Workflow.objects.get(id=self.kwargs.get("pk"))
        serializer = TransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(workflow=instance)
        return Response(serializer.data)


class TransitionDetailAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = TransitionSerializer
    permission_classes = [MenuPermissionRequired]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        workflow = Custom_Workflow.objects.get(id=self.kwargs.get("pk"))
        return Custom_Transition.objects.filter(workflow=workflow)

    def get_object(self):
        transition_id = self.kwargs.get("transition_id")
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {"pk": transition_id}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
