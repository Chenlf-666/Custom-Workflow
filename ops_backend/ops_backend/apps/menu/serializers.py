# -*- coding:utf-8 -*-
from rest_framework import serializers
from .models import *
from common.Constant import MENU
from custom_workflows.models import Custom_Workflow
from common.Constant import CUSTOM_STATE


class SimpleMenuTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    label = serializers.CharField(source="name")

    class Meta:
        model = Menu
        fields = ["id", "label", "index", "children", "workflow_id"]

    def __init__(self, *args, **kwargs):
        self.base_menus = kwargs.pop("base_menus", None)
        super(SimpleMenuTreeSerializer, self).__init__(*args, **kwargs)

    def get_children(self, obj):
        children = Menu.objects.filter(parent=obj).distinct() & self.base_menus.distinct()
        children = children.distinct().order_by("order")
        serializer = SimpleMenuTreeSerializer(children, many=True, base_menus=self.base_menus)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not representation.get("children"):
            representation.pop("children", None)
        if not representation.get("workflow_id"):
            representation.pop("workflow_id", None)
        return representation


def add_custom_workflow(result):
    active_workflows = Custom_Workflow.objects.filter(is_active=True).filter(
        status_list__state_type=CUSTOM_STATE.TYPE.Init).order_by("id")
    for label_info in result:
        if label_info.get("label") == "工作台":
            children = label_info.get("children", [])
            for workflow in active_workflows:
                workflow_info = {
                    "id": None,
                    "workflow_id": workflow.id,
                    "label": workflow.name,
                    "index": "worksheet"
                }
                children.append(workflow_info)


class MenuTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    label = serializers.CharField(source="name")

    class Meta:
        model = Menu
        fields = ["id", "label", "order", "children", "parent", "index"]

    def get_children(self, obj):
        children = Menu.objects.filter(parent=obj).order_by("order")
        serializer = MenuTreeSerializer(children, many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if not representation.get("parent"):
            representation.pop("parent", None)
        if not representation.get("children"):
            representation.pop("children", None)
        return representation


class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = "__all__"


def update_menu_data():
    old_menu_names = [item.name for item in Menu.objects.filter(workflow_id__isnull=True)]
    new_menu_names = []

    def create_data(data, parent=None):
        for name, value in data.items():
            obj, _ = Menu.objects.update_or_create(
                defaults={
                    "order": value.get("order"),
                    "parent": parent,
                    "urls": value.get("urls", None),
                    "index": value.get("index", None)
                },
                name=name
            )
            new_menu_names.append(name)
            if value.get("leaf"):
                create_data(value.get("leaf"), obj)

    create_data(MENU.TREE)
    deleted_names = list(set(old_menu_names) - set(new_menu_names))
    for delete_name in deleted_names:
        Menu.objects.filter(name=delete_name).delete()
