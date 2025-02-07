# -*- coding:utf-8 -*-
import ast
import json

from rest_framework import serializers
from users.models import User, Ops_Group
from .models import *
from menu.models import Menu
from auditlog.models import ContentType
from common.Constant import CUSTOM_STATE, MENU, CUSTOM_FIELD_TYPE


class CustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Custom_Field
        fields = ["id", "name", "field_type", "field_key", "order_id", "default_value", "field_choice",
                  "foreign_type", "special_url", "required", "displayed"]

    def validate(self, attrs):
        if attrs.get("field_type") in [CUSTOM_FIELD_TYPE.Radio, CUSTOM_FIELD_TYPE.Select,
                                       CUSTOM_FIELD_TYPE.CheckBox,
                                       CUSTOM_FIELD_TYPE.MultiSelect]:
            try:
                ast.literal_eval(attrs.get("field_choice"))
            except SyntaxError:
                raise serializers.ValidationError("字段选项解析错误，必须为json格式")
            except ValueError:
                raise serializers.ValidationError("字段选项解析错误，必须为json格式")
        return attrs


class ContentTypeSerializer(serializers.ModelSerializer):
    model_name = serializers.SerializerMethodField()

    class Meta:
        model = ContentType
        fields = "__all__"

    def get_model_name(self, obj):
        return obj.name


class StatusSerializer(serializers.ModelSerializer):
    field_info = serializers.PrimaryKeyRelatedField(queryset=Custom_Field.objects.all(), many=True, write_only=True,
                                                    required=False)
    participant_names = serializers.SerializerMethodField(read_only=True)
    participant = serializers.ListField(write_only=True)
    participant_ids = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Custom_State
        fields = ["id", "name", "order_id", "state_type", "enable_retreat", "participant_type", "participant",
                  "participant_ids", "participant_names", "field_info"]

    def get_participant_ids(self, obj):
        if obj.participant:
            return json.loads(obj.participant)
        else:
            return []

    def validate(self, attrs):
        if attrs.get("participant"):
            participant = attrs.get("participant")
            if attrs.get("participant_type") == CUSTOM_STATE.PARTICIPANT_TYPE.Field and len(participant) > 1:
                raise serializers.ValidationError("不可对应多个自定义字段")
            attrs["participant"] = str(participant)
        return attrs

    def get_participant_names(self, obj):
        if obj.participant:
            participant_ids = json.loads(obj.participant)
        else:
            return None

        if obj.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.User:
            participant_objs = User.objects.filter(id__in=participant_ids)
            participant_names = [participant.fullname() for participant in participant_objs]
        elif obj.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.Role:
            participant_objs = Ops_Group.objects.filter(id__in=participant_ids)
            participant_names = [participant.name for participant in participant_objs]
        elif obj.participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.Field:
            participant_objs = Custom_Field.objects.filter(id__in=participant_ids)
            participant_names = [participant.name for participant in participant_objs]
        else:
            return None
        return participant_names

    def create(self, validated_data):
        state_type = validated_data.get("state_type", CUSTOM_STATE.TYPE.Init)
        workflow = validated_data.get("workflow")
        if state_type == CUSTOM_STATE.TYPE.Init:
            if workflow.status_list.filter(state_type=CUSTOM_STATE.TYPE.Init):
                raise serializers.ValidationError("已存在初始类型的自定义状态")
        state_fields = validated_data.pop("field_info", [])
        instance = super(StatusSerializer, self).create(validated_data)
        for state_field in state_fields:
            # custom_field = workflow.field_list.filter(id=state_field.get("id")).first()
            Status_Field.objects.create(
                state=instance,
                field=state_field
            )
        return instance


class SimpleCusFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Custom_Field
        fields = ["id", "name"]


class SimpleTransitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Custom_Transition
        fields = ["id", "name", "alert_enable", "alert_text"]


class StatusDetailSerializer(StatusSerializer):
    fields = CustomFieldSerializer(many=True, read_only=True)
    transitions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Custom_State
        fields = ["id", "name", "order_id", "state_type", "enable_retreat", "participant_type", "participant",
                  "participant_ids", "participant_names", "field_info", "fields", "transitions"]

    def get_transitions(self, obj):
        transitions = Custom_Transition.objects.filter(source_state=obj)
        return SimpleTransitionSerializer(transitions, many=True).data

    # def to_representation(self, instance):
    #     representation = super(StatusDetailSerializer, self).to_representation(instance)
    #     fields = representation.get("fields")
    #     for field in fields:
    #         custom_field = instance.fields.get(id=field.get("id"))
    #         state_field_relation = Status_Field.objects.get(state=instance, field=custom_field)
    #         field["required"] = state_field_relation.required
    #     return representation

    def update(self, instance, validated_data):
        state_type = validated_data.get("state_type", CUSTOM_STATE.TYPE.Init)
        workflow = instance.workflow
        if state_type == CUSTOM_STATE.TYPE.Init:
            if workflow.status_list.exclude(id=instance.id).filter(state_type=CUSTOM_STATE.TYPE.Init):
                raise serializers.ValidationError("已存在初始类型的自定义状态")
        new_fields = validated_data.pop("field_info", [])
        new_field_relations = []
        old_field_relations = instance.fields.all()
        for new_field in new_fields:
            instance.fields.add(new_field)
            new_field_relations.append(new_field)
        for old_field_relation in old_field_relations:
            if old_field_relation not in new_field_relations:
                instance.fields.remove(old_field_relation)

        return super(StatusSerializer, self).update(instance, validated_data)


class CustomWorkflowSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(source="creator.fullname", read_only=True)

    class Meta:
        model = Custom_Workflow
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["creator"] = user
        if Menu.objects.filter(name=validated_data.get("name")):
            raise serializers.ValidationError("工作流名称不可和已有菜单同名")
        instance = super(CustomWorkflowSerializer, self).create(validated_data)
        if instance.is_active and Menu.objects.filter(name=MENU.ApprovalProcess):
            parent_menu = Menu.objects.get(name=MENU.ApprovalProcess)
            Menu.objects.create(
                name=instance.name,
                parent=parent_menu,
                order=(parent_menu.leaves.aggregate(Max('order'))['order__max'] or 0) + 1,
                index="/worksheet" + str(instance.id),
                urls="/worksheet.*",
                workflow_id=instance.id
            )
        return instance

    def update(self, instance, validated_data):
        if Menu.objects.exclude(name=instance.name).filter(name=validated_data.get("name")):
            raise serializers.ValidationError("工作流名称不可和已有菜单同名")
        if Menu.objects.filter(name=MENU.ApprovalProcess):
            parent_menu = Menu.objects.get(name=MENU.ApprovalProcess)
            if validated_data.get("is_active"):
                if parent_menu.leaves.filter(name=instance.name):
                    if validated_data.get("name") != instance.name:
                        parent_menu.leaves.filter(name=instance.name).update(name=validated_data.get("name"))
                else:
                    Menu.objects.update_or_create(
                        name=validated_data.get("name"),
                        parent=parent_menu,
                        order=(parent_menu.leaves.aggregate(Max('order'))['order__max'] or 0) + 1,
                        index="/worksheet" + str(instance.id),
                        urls="/worksheet.*",
                        workflow_id=instance.id
                    )
            else:
                if parent_menu.leaves.filter(name=instance.name):
                    parent_menu.leaves.filter(name=instance.name).delete()
        return super(CustomWorkflowSerializer, self).update(instance, validated_data)


class TriggerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Custom_Trigger
        fields = ["id", "type", "name"]

    def get_name(self, obj):
        if obj.type == 1:
            return "发送消息给后续人员"


class TransitionSerializer(serializers.ModelSerializer):
    source_state_name = serializers.CharField(source="source_state.name", read_only=True)
    dest_state_name = serializers.CharField(source="dest_state.name", read_only=True)
    triggers = TriggerSerializer(many=True, read_only=True)
    trigger_types = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Custom_Transition
        fields = ["id", "name", "source_state", "dest_state", "alert_enable", "alert_text",
                  "trans_type", "source_state_name", "dest_state_name", "triggers", "trigger_types"]

    def validate(self, attrs):
        if not attrs.get("source_state") or not attrs.get("dest_state"):
            raise serializers.ValidationError("源状态或目的状态不可同时为空")
        return attrs

    def create(self, validated_data):
        trigger_types = validated_data.pop("trigger_types", [])
        instance = super().create(validated_data)
        for trigger_type in trigger_types:
            Custom_Trigger.objects.create(transition=instance, type=trigger_type)
        return instance

    def update(self, instance, validated_data):
        trigger_types = validated_data.pop("trigger_types", [])
        old_triggers = instance.triggers.all()
        old_trigger_types = [old_trigger.type for old_trigger in old_triggers]
        for trigger_type in trigger_types:
            if trigger_type not in old_trigger_types:
                Custom_Trigger.objects.create(transition=instance, type=trigger_type)
        for old_trigger_type in old_trigger_types:
            if old_trigger_type not in trigger_types:
                instance.triggers.filter(type=old_trigger_type).delete()
        return super(TransitionSerializer, self).update(instance, validated_data)


class RelateUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='fullname', read_only=True)

    class Meta:
        model = User
        fields = ["id", "name"]


class RelateGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ops_Group
        fields = ["id", "name"]
