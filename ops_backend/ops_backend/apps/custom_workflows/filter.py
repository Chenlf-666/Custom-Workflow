# -*- coding:utf-8 -*-

import django_filters
from django_filters.rest_framework import FilterSet
from django.db.models import Q
from . import models
from common.Constant import CUSTOM_STATE


class CustomWorkflowFilter(FilterSet):
    name = django_filters.CharFilter(method="name_filter")
    usable = django_filters.BooleanFilter(method="active_filter")

    class Meta:
        model = models.Custom_Workflow
        fields = ["name", "usable"]

    @staticmethod
    def name_filter(queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(description__icontains=value))

    @staticmethod
    def active_filter(queryset, name, value):
        if value:
            return queryset.filter(is_active=True).filter(status_list__state_type=CUSTOM_STATE.TYPE.Init)
        return queryset.filter(is_active=False).union(queryset.filter(is_active=True).exclude(status_list__state_type=CUSTOM_STATE.TYPE.Init))


class CustomFieldFilter(FilterSet):
    name = django_filters.CharFilter(method="name_filter")

    class Meta:
        models = models.Custom_Field
        fields = ["name"]

    @staticmethod
    def name_filter(queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(field_key__icontains=value))
