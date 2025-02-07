# -*- coding:utf-8 -*-
import json

import pytz
from datetime import timedelta, datetime, time

from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from .serializers import *
from .models import ToDo_Task


class StatByLoginAPI(GenericAPIView):
    serializer_class = BaseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        tz = pytz.timezone('Asia/Shanghai')
        today = tz.localize(datetime.combine(datetime.now(), time.min))
        count = User.objects.filter(last_login__gte=today).count()
        return Response(data={"count": count})


class ToDoTaskListAPI(ListCreateAPIView):
    queryset = ToDo_Task.objects.all().order_by('completed', '-update_time')
    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        owner = request.user
        tz = pytz.timezone('Asia/Shanghai')
        startDate = tz.localize(datetime.now()-timedelta(days=30))
        queryset = queryset.filter(update_time__gte=startDate, owner=owner)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)