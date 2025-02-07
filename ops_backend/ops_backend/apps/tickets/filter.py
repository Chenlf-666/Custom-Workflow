# -*- coding:utf-8 -*-

import django_filters
from django_filters.rest_framework import FilterSet
from django.db.models import Q
from . import models
from custom_workflows.models import Custom_Workflow
from common.Constant import CUSTOM_STATE


class TicketFilter(FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    workflow = django_filters.ModelChoiceFilter(queryset=Custom_Workflow.objects.all())
    completed = django_filters.BooleanFilter(method="completed_filter")

    class Meta:
        model = models.Ticket
        fields = ["name", "workflow", "completed"]

    def completed_filter(self, queryset, name, value):
        value = bool(value)
        if value:
            return queryset.filter(status__state_type=CUSTOM_STATE.TYPE.End)
        return queryset.exclude(status__state_type=CUSTOM_STATE.TYPE.End)
