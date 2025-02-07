# -*- coding:utf-8 -*-
import json
from rest_framework import serializers
from .models import *
from custom_workflows.serializers import CustomFieldSerializer, SimpleTransitionSerializer
from common.Constant import CUSTOM_FIELD_TYPE
from common.Util import get_displayed_value, get_selected_value


class TicketFieldSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source="custom_field.name", read_only=True)
    field_key = serializers.CharField(source="custom_field.field_key", read_only=True)
    field_type = serializers.IntegerField(source="custom_field.field_type", read_only=True)
    display_value = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ticket_Field
        fields = ["id", "custom_field", "field_name", "field_key", "field_value", "field_type", "display_value"]

    def get_display_value(self, obj):
        field = obj.custom_field
        if obj.field_value:
            if field.field_type == CUSTOM_FIELD_TYPE.Foreign:
                id_list = [obj.field_value]
            elif field.field_type == CUSTOM_FIELD_TYPE.MultiForeign:
                id_list = json.loads(obj.field_value)
            elif field.field_type in [CUSTOM_FIELD_TYPE.Radio, CUSTOM_FIELD_TYPE.Select, CUSTOM_FIELD_TYPE.CheckBox,
                                      CUSTOM_FIELD_TYPE.MultiSelect]:
                return get_selected_value(obj.field_value, field.field_choice)
            else:
                return obj.field_value
            foreign_type = field.foreign_type
            model_class = foreign_type.model_class()
            if model_class == User:
                name_list = [item.fullname() for item in model_class.objects.filter(id__in=id_list)]
            else:
                name_list = [item.name for item in model_class.objects.filter(id__in=id_list)]
            return "、".join(name_list)


class StatusOperatorSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="operator.id")
    name = serializers.CharField(source="operator.fullname", read_only=True)

    class Meta:
        model = Ticket_Operator
        read_only_fields = ["is_confirm"]
        fields = ["id", "name", "is_confirm"]


class TicketStatusSerializer(serializers.ModelSerializer):
    fields = serializers.SerializerMethodField(read_only=True, method_name="get_status_fields")
    users = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, ticket=None, **kwargs):
        super(TicketStatusSerializer, self).__init__(*args, **kwargs)
        self.ticket = ticket

    class Meta:
        model = Custom_State
        fields = ["id", "name", "fields", "users"]

    def get_status_fields(self, obj):
        state_fields = obj.fields.all()
        ticket_fields = self.ticket.fields.filter(custom_field__in=state_fields).select_related("custom_field")
        if ticket_fields:
            return TicketFieldSerializer(ticket_fields, many=True).data
        else:
            return CustomFieldSerializer(state_fields, many=True).data

    def get_users(self, obj):
        query_set = self.ticket.users.filter(status=obj).select_related("operator")
        return StatusOperatorSerializer(query_set, many=True).data


class TicketLogSerializer(serializers.ModelSerializer):
    transition_name = serializers.SerializerMethodField(read_only=True)
    source_state = serializers.CharField(source="transition.source_state.name", read_only=True)
    dest_state = serializers.CharField(source="transition.dest_state.name", read_only=True)
    # create_time = serializers.SerializerMethodField()

    class Meta:
        model = Ticket_Log
        fields = ["id", "suggestion", "transition_name", "participant", "create_time", "source_state", "dest_state"]

    def get_create_time(self, obj):
        return obj.create_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_transition_name(self, obj):
        if obj.transition:
            return obj.transition.name
        return obj.suggestion


class TicketSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    creator = serializers.CharField(source="creator.fullname", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)
    workflow = serializers.PrimaryKeyRelatedField(queryset=Custom_Workflow.objects.all())
    workflow_name = serializers.CharField(source="workflow.name", read_only=True)
    operators = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ticket
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        instance = super(TicketSerializer, self).create(validated_data)
        return instance

    def get_operators(self, obj):
        custom_state = obj.status
        if custom_state.state_type == CUSTOM_STATE.TYPE.Init:
            return [obj.creator.fullname()]
        if obj.users.filter(status=obj.status):
            return [status_operator.operator.fullname() for status_operator in obj.users.filter(status=obj.status).select_related("operator")]
        return []


class TicketListSerializer(TicketSerializer):
    display_values = serializers.SerializerMethodField(read_only=True)
    status_process = serializers.SerializerMethodField(read_only=True)

    def get_display_values(self, obj):
        display_values = []
        for ticket_field in obj.fields.select_related("custom_field").order_by("custom_field__order_id"):
            custom_field = ticket_field.custom_field
            if custom_field.displayed:
                item = {}
                if ticket_field.field_value:
                    item[custom_field.name] = get_displayed_value(custom_field, ticket_field.field_value)
                else:
                    item[custom_field.name] = "N/A"

                display_values.append(item)
        return display_values

    def get_status_process(self, obj):
        status = obj.status
        workflow = obj.workflow
        if status.state_type == CUSTOM_STATE.TYPE.End:
            return 100
        max_process = workflow.status_list.aggregate(Max("order_id")).get("order_id__max")
        return round(status.order_id / max_process * 100)


class TicketDetailSerializer(TicketSerializer):
    status_list = serializers.SerializerMethodField(read_only=True)
    transitions = serializers.SerializerMethodField(read_only=True)

    def get_status_list(self, obj):
        workflow = obj.workflow
        status_list = workflow.status_list.order_by("order_id")
        return TicketStatusSerializer(status_list, many=True, ticket=obj).data

    def get_transitions(self, obj):
        workflow = obj.workflow
        transition_list = workflow.custom_transition_set.filter(source_state=obj.status)
        return SimpleTransitionSerializer(transition_list, many=True).data


class TicketCurrentFieldValueSerializer(CustomFieldSerializer):
    default_value = serializers.SerializerMethodField()

    def __init__(self, *args, ticket=None, **kwargs):
        super(TicketCurrentFieldValueSerializer, self).__init__(*args, **kwargs)
        self.ticket = ticket

    def get_default_value(self, obj):
        if self.ticket.fields.filter(custom_field=obj):
            ticket_field = self.ticket.fields.filter(custom_field=obj).first()
            return ticket_field.field_value
        return obj.default_value


class TicketCurrentFieldsSerializer(TicketSerializer):
    current_fields = serializers.SerializerMethodField(read_only=True)
    transitions = serializers.SerializerMethodField(read_only=True)
    enable_retreat = serializers.BooleanField(source="status.enable_retreat", read_only=True, default=False)

    def get_current_fields(self, obj):
        custom_state = obj.status
        state_fields = custom_state.fields.all()
        return TicketCurrentFieldValueSerializer(state_fields, many=True, ticket=obj).data

    def get_transitions(self, obj):
        workflow = obj.workflow
        transition_list = workflow.custom_transition_set.filter(source_state=obj.status)
        return SimpleTransitionSerializer(transition_list, many=True).data
