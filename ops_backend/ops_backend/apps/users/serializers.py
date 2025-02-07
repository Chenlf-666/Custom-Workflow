from datetime import datetime, timedelta
from rest_framework import serializers
from auditlog.models import LogEntry
from django.contrib.auth.models import Permission

from .models import *
from menu.models import Menu
from menu.serializers import SimpleMenuTreeSerializer, add_custom_workflow


class UserSerializer(serializers.ModelSerializer):
    """用户详情序列化器"""
    pwd_expire_date = serializers.SerializerMethodField(read_only=True, default=None)
    name = serializers.CharField(source='fullname', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'fullname', 'name', 'email', 'is_superuser', 'is_staff',
                  'is_active', 'role', 'mobile', 'last_login', 'pwd_expire_date']

    def get_pwd_expire_date(self, obj):
        if obj.reset_pwd_stamp:
            pwd_last_set_timestamp = (int(obj.reset_pwd_stamp) / 10000000) - 11644473600
            # 将时间戳转换为日期时间对象
            timestamp_datetime = datetime.utcfromtimestamp(pwd_last_set_timestamp)
            expire_datetime = timestamp_datetime + timedelta(days=90)
            date = expire_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            return date


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'fullname']


class LogEntrySerializer(serializers.ModelSerializer):
    model = serializers.CharField(source="content_type.model")
    operator = serializers.CharField(source="actor.fullname", read_only=True, default="system")
    changes = serializers.DictField(source="changes_display_dict", read_only=True)

    class Meta:
        model = LogEntry
        fields = ['timestamp', 'operator', 'object_id', 'object_repr', 'model', 'action', 'remote_addr', 'changes']


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    users = SimpleUserSerializer(source="user_set", many=True, read_only=True)
    user_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)
    menu_permissions = serializers.PrimaryKeyRelatedField(queryset=Menu.objects.all(), many=True, write_only=True)

    class Meta:
        model = Ops_Group
        fields = ["id", "name", "desc", "users", "user_ids", "desc", "create_time", "update_time", "menu_permissions"]

    def create(self, validated_data):
        validated_data["user_set"] = validated_data.pop("user_ids", [])
        return super(GroupSerializer, self).create(validated_data)


class SimpleMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'index']


class GroupDetailSerializer(GroupSerializer):
    authed_menus = SimpleMenuSerializer(source="menu_permissions", many=True, read_only=True)

    class Meta:
        model = Ops_Group
        fields = ["id", "name", "desc", "users", "user_ids", "desc", "create_time", "update_time", "menu_permissions", "authed_menus"]

    def update(self, instance, validated_data):
        new_users = validated_data.pop("user_ids", [])
        old_users = [item for item in instance.user_set.all()]
        add_users = list(set(new_users) - set(old_users))
        remove_users = list(set(old_users) - set(new_users))
        for add_user in add_users:
            add_user.groups.add(instance)
        for remove_user in remove_users:
            remove_user.groups.remove(instance)
        return super(GroupDetailSerializer, self).update(instance, validated_data)


class UserProfileSerializer(UserSerializer):
    authed_menus = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'fullname', 'email', 'is_superuser', 'is_staff',
                  'is_active', 'role', 'mobile', 'last_login', 'pwd_expire_date', 'authed_menus']

    def get_authed_menus(self, obj):
        authed_groups = Ops_Group.objects.filter(group_ptr__in=obj.groups.all())
        if obj.is_staff:
            query_set = Menu.objects.all()
            parent_query_set = Menu.objects.filter(parent__isnull=True).order_by("order").distinct()
        else:
            query_set = Menu.objects.filter(ops_group__in=authed_groups)
            parent_query_set = Menu.objects.filter(ops_group__in=authed_groups, parent__isnull=True).order_by("order").distinct()
        result = SimpleMenuTreeSerializer(parent_query_set, many=True, base_menus=query_set).data
        # add_custom_workflow(result)
        return result

