# -*- coding:utf-8 -*-
import django_filters
from django_filters.rest_framework import FilterSet
from django.db.models import Q
from . import models
from auditlog.models import LogEntry


class UserFilter(FilterSet):
    name = django_filters.CharFilter(method="name_filter")

    class Meta:
        model = models.User
        fields = ["name"]

    @staticmethod
    def name_filter(queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) | Q(email__icontains=value) | Q(first_name__icontains=value) | Q(last_name__icontains=value))


class AuditLogFilter(FilterSet):
    ACTION_CHOICE = (
        (0, "create"),
        (1, "update"),
        (2, "delete"),
        (3, "access"),
    )
    action = django_filters.ChoiceFilter(field_name="action", choices=ACTION_CHOICE)
    actor = django_filters.ModelChoiceFilter(queryset=models.User.objects.all())

    class Meta:
        models = LogEntry
        fields = ["action", "actor"]


class GroupFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        models = models.Ops_Group
        fields = ["name"]
