# -*- coding:utf-8 -*-
import traceback
from rest_framework import serializers
from users.models import User
from .models import *
from common.Constant import TODO_TYPE, MENU
from tickets.models import Ticket
from menu.models import Menu


class StatByUserSerializer(serializers.Serializer):
    owner_name = serializers.SerializerMethodField()
    count = serializers.IntegerField()
    pending = serializers.IntegerField()
    success = serializers.IntegerField()
    failure = serializers.IntegerField()
    aborted = serializers.IntegerField()
    timeout = serializers.IntegerField()

    def get_owner_name(self, obj):
        user_id = obj["owner"]
        if user_id:
            user = User.objects.get(id=user_id)
            return user.fullname()
        return "Timer"


class TodoSerializer(serializers.ModelSerializer):
    reference_name = serializers.SerializerMethodField(read_only=True)
    order = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ToDo_Task
        fields = ["type", "update_time", "completed", "reference_id", "reference_name", "order"]

    def get_reference_name(self, obj):
        if obj.type == TODO_TYPE.CheckTicket and obj.reference_id:
            ticket = Ticket.objects.get(id=obj.reference_id)
            custom_workflow = ticket.workflow
            if ticket.name:
                return custom_workflow.name + " - " + ticket.name
            return custom_workflow.name

    def get_order(self, obj):
        if obj.type == TODO_TYPE.CheckTicket and obj.reference_id:
            try:
                ticket = Ticket.objects.get(id=obj.reference_id)
                custom_workflow = ticket.workflow
                custom_workflow_ids = [menu.workflow_id for menu in Menu.objects.filter(parent__name=MENU.ApprovalProcess).order_by("order")]
                web_order = custom_workflow_ids.index(custom_workflow.id)
                return web_order
            except Exception as e:
                print(traceback.format_exc())
        return None
