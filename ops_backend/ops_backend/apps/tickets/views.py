# -*- coding:utf-8 -*-
import traceback

import coreschema
import re
from coreapi import Field

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.schemas import AutoSchema
from .filter import *
from .serializers import *
from .models import *
from .utils import handle_trigger, logger, thread_send_msg_to_user_group
from common.Constant import CUSTOM_STATE, CUSTOM_TRANSITION, TODO_TYPE
from common.Util import check_todo_list

from auditlog.models import ContentType
from users.models import User, Ops_Group
from dashboard.models import ToDo_Task


class TicketListCreateAPI(ListCreateAPIView):
    queryset = Ticket.objects.all().select_related("creator", "workflow", "status").order_by("-update_time")
    permission_classes = [IsAuthenticated]
    filterset_class = TicketFilter
    schema = AutoSchema([Field(name="category", required=False, location="query", schema=coreschema.String())])

    def get_serializer_class(self):
        return TicketListSerializer

    def get_duty_query(self, queryset, user):
        pending_id_list = []
        for ticket in queryset:
            current_status = ticket.status
            if current_status.state_type == CUSTOM_STATE.TYPE.Normal \
                    and current_status.participant_type != CUSTOM_STATE.PARTICIPANT_TYPE.Empty:
                if current_status.participant and current_status.participant != "[]":
                    try:
                        participant_ids = json.loads(current_status.participant)
                        if isinstance(participant_ids, int):
                            participant_ids = [participant_ids]
                        if current_status.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.Role:
                            participant_objs = Ops_Group.objects.filter(id__in=participant_ids)
                            if participant_objs & user.groups.all():
                                pending_id_list.append(ticket.id)
                        else:
                            if ticket.users.filter(status=current_status, operator=user, is_confirm=False):
                                pending_id_list.append(ticket.id)
                    except json.decoder.JSONDecodeError:
                        continue
            elif current_status.state_type == CUSTOM_STATE.TYPE.Init and ticket.creator == user:
                # 避免驳回的工单看不到
                pending_id_list.append(ticket.id)
        queryset = queryset.filter(id__in=pending_id_list)
        return queryset

    def list(self, request, *args, **kwargs):
        user = request.user
        category = request.GET.get("category")
        queryset = self.filter_queryset(self.get_queryset())
        if category == "owner":
            # 创建的工单
            queryset = queryset.filter(creator=user)
        elif category == "duty":
            # 待办的工单
            queryset = self.get_duty_query(queryset, user)
        elif category == "worked":
            # 处理过的工单
            queryset = queryset.filter(ticket_log__participant=user.fullname()).distinct()
        else:
            if not user.is_staff and not user.is_superuser:
                owner_queryset = queryset.filter(creator=user)
                duty_queryset = self.get_duty_query(queryset, user)
                worked_queryset = queryset.filter(ticket_log__participant=user.fullname())
                queryset = (owner_queryset | duty_queryset | worked_queryset).distinct().order_by("-update_time")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        transition_id = request.data.pop("transition", None)
        workflow_id = request.data.pop("workflow", None)
        if workflow_id is None:
            return Response(data={"message": "workflow不可为空"}, status=status.HTTP_400_BAD_REQUEST)
        if transition_id is None:
            return Response(data={"message": "transition不可为空"}, status=status.HTTP_400_BAD_REQUEST)
        workflow = Custom_Workflow.objects.get(id=workflow_id)
        for check_field in workflow.field_list.filter(field_key__in=request.data.keys()):
            if check_field.required and request.data.get(check_field.field_key) is None:
                return Response(data={"message": "{}字段不可为空".format(check_field.name)}, status=status.HTTP_400_BAD_REQUEST)
        transition = Custom_Transition.objects.get(id=transition_id)
        dest_state = transition.dest_state
        ticket_info = {
            "name": request.data.pop("name"),
            "workflow": workflow_id,
            "status": dest_state.id
        }
        serializer = self.get_serializer(data=ticket_info)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        headers = self.get_success_headers(serializer.data)

        for key, value in request.data.items():
            try:
                field = workflow.field_list.get(field_key=key)
                Ticket_Field.objects.update_or_create(
                    defaults={
                        "field_value": value
                    },
                    ticket=ticket,
                    custom_field=field
                )
            except Custom_Field.DoesNotExist:
                logger.error("custom_field ({}: {}) not found".format(key, value))
                continue

        Ticket_Log.objects.create(
            ticket=ticket,
            transition=transition,
            participant=user.fullname()
        )
        participant_ids = json.loads(dest_state.participant)
        if isinstance(participant_ids, int):
            participant_ids = [participant_ids]
        if dest_state.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.User:
            operator_objs = User.objects.filter(id__in=participant_ids)
            for operator in operator_objs:
                Ticket_Operator.objects.create(
                    ticket=ticket,
                    status=dest_state,
                    operator=operator
                )
                ToDo_Task.objects.create(
                    type=TODO_TYPE.CheckTicket,
                    reference_id=ticket.id,
                    owner=operator
                )
        elif dest_state.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.Field:
            field_id = participant_ids[0]
            field_obj = Custom_Field.objects.get(id=field_id)
            if ticket.fields.filter(custom_field=field_obj):
                ticket_field = ticket.fields.get(custom_field=field_obj)
                ticket_field_value = ticket_field.field_value
                value_ids = json.loads(ticket_field_value)
                if isinstance(value_ids, int):
                    value_ids = [value_ids]
                relate_users = User.objects.filter(id__in=value_ids)
                for operator in relate_users:
                    Ticket_Operator.objects.create(
                        ticket=ticket,
                        status=dest_state,
                        operator=operator
                    )
                    ToDo_Task.objects.create(
                        type=TODO_TYPE.CheckTicket,
                        reference_id=ticket.id,
                        owner=operator
                    )

        if transition.triggers.all():
            handle_trigger(ticket, transition)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TicketDetailAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = TicketDetailSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        return Ticket.objects.filter(id=self.kwargs.get("pk"))

    def put(self, request, *args, **kwargs):
        user = request.user
        transition_id = request.data.pop("transition", None)
        workflow_id = request.data.pop("workflow", None)
        if workflow_id is None:
            return Response(data={"message": "workflow不可为空"}, status=status.HTTP_400_BAD_REQUEST)
        workflow = Custom_Workflow.objects.get(id=workflow_id)
        ticket_info = {
            "name": request.data.pop("name")
        }
        instance = self.get_object()
        if user != instance.creator:
            return Response(data={"message": "无权限"}, status=status.HTTP_403_FORBIDDEN)
        if instance.workflow != workflow:
            return Response(data={"message": "workflow不可更改"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(instance, data=ticket_info, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        for key, value in request.data.items():
            field = workflow.field_list.get(field_key=key)
            Ticket_Field.objects.update_or_create(
                defaults={
                    "field_value": value
                },
                ticket=instance,
                custom_field=field
            )
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        ToDo_Task.objects.filter(type=TODO_TYPE.CheckTicket, reference_id=instance.id).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TicketLogAPI(ListCreateAPIView):
    serializer_class = TicketLogSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get_queryset(self):
        ticket = Ticket.objects.get(id=self.kwargs.get("pk"))
        return Ticket_Log.objects.filter(ticket=ticket).order_by("create_time")


class TicketCurrentStateFieldsAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = TicketCurrentFieldsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get_queryset(self):
        return Ticket.objects.filter(id=self.kwargs.get("pk"))


class TicketHandleAPI(ListCreateAPIView):
    serializer_class = BaseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]
    handle_type = None
    schema = AutoSchema([
        Field(name="transition", required=True, location="form", schema=coreschema.Integer()),
        Field(name="suggestion", required=False, location="form", schema=coreschema.String()),
    ])

    def get_queryset(self):
        return Ticket.objects.filter(id=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        user = request.user
        ticket = self.get_object()
        workflow = ticket.workflow
        suggestion = request.data.pop("suggestion", None)
        transition_id = request.data.pop("transition", None)
        if transition_id is None:
            return Response(data={"message": "transition不可为空"}, status=status.HTTP_400_BAD_REQUEST)
        transition = Custom_Transition.objects.get(id=transition_id)
        source_state = transition.source_state
        dest_state = transition.dest_state
        if ticket.status.state_type == CUSTOM_STATE.TYPE.Init and user != ticket.creator:
            return Response(data={"message": "无操作权限"}, status=status.HTTP_403_FORBIDDEN)
        if ticket.users.filter(status=source_state, operator=user, is_confirm=True):
            return Response(data={"message": "您已处理过该任务"}, status=status.HTTP_400_BAD_REQUEST)
        if source_state.participant_type != CUSTOM_STATE.PARTICIPANT_TYPE.Empty:
            if source_state.participant and source_state.participant != "[]":
                try:
                    participant_ids = json.loads(source_state.participant)
                    if isinstance(participant_ids, int):
                        participant_ids = [participant_ids]
                    if source_state.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.Role:
                        participant_objs = Ops_Group.objects.filter(id__in=participant_ids)
                        if not (participant_objs & user.groups.all()):
                            return Response(data={"message": "无操作权限"}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        if not ticket.users.filter(status=source_state, operator=user):
                            return Response(data={"message": "无操作权限"}, status=status.HTTP_403_FORBIDDEN)
                    Ticket_Operator.objects.update_or_create(
                        defaults={
                            "is_confirm": True
                        },
                        ticket=ticket,
                        status=source_state,
                        operator=user
                    )
                except json.decoder.JSONDecodeError:
                    logger.error(traceback.format_exc())
                except Custom_Field.DoesNotExist:
                    logger.error("custom_field not found")
                except Ticket_Field.DoesNotExist:
                    logger.error("ticket_field not found")

        if source_state != ticket.status:
            return Response(data={"message": "当前状态不可进行{}操作".format(transition.name)}, status=status.HTTP_400_BAD_REQUEST)
        for check_field in workflow.field_list.filter(field_key__in=request.data.keys()):
            if check_field.required and request.data.get(check_field.field_key) is None:
                return Response(data={"message": "{}字段不可为空".format(check_field.name)}, status=status.HTTP_400_BAD_REQUEST)

        for key, value in request.data.items():
            try:
                field = workflow.field_list.get(field_key=key)
                Ticket_Field.objects.update_or_create(
                    defaults={
                        "field_value": value
                    },
                    ticket=ticket,
                    custom_field=field
                )
            except Custom_Field.DoesNotExist:
                logger.error("custom_field ({}: {}) not found".format(key, value))
                continue
        Ticket_Log.objects.create(
            ticket=ticket,
            suggestion=suggestion,
            transition=transition,
            participant=user.fullname()
        )
        # 如果源状态和目标状态不一样，判断是否流转到下一状态，将下一状态的操作者改为未确认
        if source_state != dest_state:
            participant_ids = json.loads(dest_state.participant)
            if isinstance(participant_ids, int):
                participant_ids = [participant_ids]
            if dest_state.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.User:
                operator_objs = User.objects.filter(id__in=participant_ids)
                for operator in operator_objs:
                    Ticket_Operator.objects.update_or_create(
                        defaults={
                            "is_confirm": False
                        },
                        ticket=ticket,
                        status=dest_state,
                        operator=operator
                    )
            elif dest_state.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.Field:
                field_id = participant_ids[0]
                field_obj = Custom_Field.objects.get(id=field_id)
                if ticket.fields.filter(custom_field=field_obj):
                    ticket_field = ticket.fields.get(custom_field=field_obj)
                    ticket_field_value = ticket_field.field_value
                    value_ids = json.loads(ticket_field_value)
                    if isinstance(value_ids, int):
                        value_ids = [value_ids]
                    relate_users = User.objects.filter(id__in=value_ids)
                    for operator in relate_users:
                        Ticket_Operator.objects.update_or_create(
                            defaults={
                                "is_confirm": False
                            },
                            ticket=ticket,
                            status=dest_state,
                            operator=operator
                        )
            if source_state.order_id > dest_state.order_id:
                # 如果是驳回操作，将源状态的处理人去掉
                ticket.users.filter(status=source_state).delete()
            if source_state.participant_type in [CUSTOM_STATE.PARTICIPANT_TYPE.Role, CUSTOM_STATE.PARTICIPANT_TYPE.Empty] or \
                    (source_state.participant_type in [CUSTOM_STATE.PARTICIPANT_TYPE.User, CUSTOM_STATE.PARTICIPANT_TYPE.Field]
                     and transition.trans_type == CUSTOM_TRANSITION.TRANS_TYPE.Single):
                # 处理人为空或者角色，或者只需要单人处理
                ticket.status = dest_state
                ticket.save()
                if transition.triggers.all():
                    handle_trigger(ticket, transition)
            else:
                if not ticket.users.filter(status=source_state, is_confirm=False):
                    # 如果需要多人处理，检查是否全部执行过，或者是否驳回操作，驳回把所有操作人确认改为false
                    ticket.status = dest_state
                    ticket.save()
                    if transition.triggers.all():
                        handle_trigger(ticket, transition)
        check_todo_list(source_state, ticket.id, TODO_TYPE.CheckTicket)
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


class TicketAssignAPI(ListCreateAPIView):
    serializer_class = BaseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]
    schema = AutoSchema([
        Field(name="user_ids", required=True, location="form", schema=coreschema.Array()),
    ])

    def get_queryset(self):
        return Ticket.objects.filter(id=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        user = request.user
        ticket = self.get_object()
        if ticket.status.state_type == CUSTOM_STATE.TYPE.Init:
            return Response(data={"message": "初始状态不可移交"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not ticket.users.filter(status=ticket.status, operator=user):
                return Response(data={"message": "无操作权限"}, status=status.HTTP_403_FORBIDDEN)
        if ticket.users.filter(status=ticket.status, operator=user, is_confirm=True):
            return Response(data={"message": "您已处理过该任务"}, status=status.HTTP_400_BAD_REQUEST)

        user_ids = request.data.get("user_ids", [])
        if len(user_ids) == 0:
            return Response(data={"message": "移交用户不可为空"}, status=status.HTTP_400_BAD_REQUEST)
        ticket.users.filter(status=ticket.status, operator=user).delete()
        for user_id in user_ids:
            assign_user = User.objects.get(id=user_id)
            new_operator, _ = Ticket_Operator.objects.get_or_create(
                ticket=ticket,
                status=ticket.status,
                operator=assign_user
            )
            users = User.objects.filter(id__in=user_ids).distinct()
            t = thread_send_msg_to_user_group(users, None, ticket)
            t.start()

        Ticket_Log.objects.create(
            ticket=ticket,
            suggestion="移交",
            participant=user.fullname()
        )
        check_todo_list(ticket.status, ticket.id, TODO_TYPE.CheckTicket)
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


class TicketRetreatAPI(ListCreateAPIView):
    serializer_class = BaseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def get_queryset(self):
        return Ticket.objects.filter(id=self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        user = request.user
        ticket = self.get_object()
        if user != ticket.creator:
            return Response(data={"message": "无操作权限"}, status=status.HTTP_403_FORBIDDEN)
        if not ticket.status.enable_retreat:
            return Response(data={"message": "该状态不可撤回"}, status=status.HTTP_400_BAD_REQUEST)
        workflow = ticket.workflow
        init_state = workflow.status_list.filter(state_type=CUSTOM_STATE.TYPE.Init).first()
        Ticket_Log.objects.create(
            ticket=ticket,
            suggestion="撤回",
            participant=user.fullname()
        )
        ticket.users.all().delete()
        ticket.status = init_state
        ticket.save()
        check_todo_list(ticket.status, ticket.id, TODO_TYPE.CheckTicket)
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


class TicketFieldRelateUrlAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = BaseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get_queryset(self):
        return Ticket.objects.filter(id=self.kwargs.get("pk"))

    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        field_id = kwargs.get("field_id")
        field = Custom_Field.objects.get(id=field_id)
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
            workflow = ticket.workflow
            for replace_key in re.findall(r'<(.*?)>', special_url):
                if workflow.field_list.filter(field_key=replace_key):
                    replace_field = workflow.field_list.get(field_key=replace_key)
                    if ticket.fields.filter(custom_field=replace_field):
                        replace_value = ticket.fields.get(custom_field=replace_field).field_value
                        special_url = special_url.replace("<{}>".format(replace_key), replace_value)
            return Response(data={"url": special_url})
        return Response(data={"url": ""})

