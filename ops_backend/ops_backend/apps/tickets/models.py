# -*- coding: utf-8 -*-
from django.db import models
from models import BaseModel
from custom_workflows.models import *
from users.models import *


class Ticket(BaseModel):
    """
    工单记录
    """
    name = models.CharField(verbose_name='标题', max_length=100, blank=True, null=True, default='')
    creator = models.ForeignKey(User, verbose_name='创建者', blank=True, null=True, on_delete=models.SET_NULL)
    workflow = models.ForeignKey(Custom_Workflow, on_delete=models.CASCADE, verbose_name='工作流')
    status = models.ForeignKey(Custom_State, on_delete=models.CASCADE, verbose_name='当前状态')

    class Meta:
        db_table = "ops_tickets"
        verbose_name = '工单记录'
        verbose_name_plural = verbose_name


class Ticket_Log(BaseModel):
    """
    工单流转日志
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name='工单')
    suggestion = models.CharField(verbose_name='审批意见', max_length=140, blank=True, null=True)
    transition = models.ForeignKey(Custom_Transition, on_delete=models.CASCADE, null=True, verbose_name='流转')
    participant = models.CharField(verbose_name='处理人', max_length=50, default='', blank=True)

    class Meta:
        db_table = "ops_ticket_log"
        verbose_name = '工单流转日志'
        verbose_name_plural = verbose_name


class Ticket_Field(BaseModel):
    """
    工单自定义字段， 工单自定义字段实际的值。
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name='工单', related_name="fields")
    custom_field = models.ForeignKey(Custom_Field, on_delete=models.CASCADE, verbose_name='字段')
    field_value = models.TextField(verbose_name='字段值', default='', blank=True)

    class Meta:
        db_table = "ops_ticket_field"
        verbose_name = '工单自定义字段值'
        verbose_name_plural = verbose_name


class Ticket_Operator(BaseModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name='工单', related_name="users")
    status = models.ForeignKey(Custom_State, on_delete=models.CASCADE, verbose_name='当前状态')
    operator = models.ForeignKey(User, verbose_name='执行人', on_delete=models.CASCADE)
    is_confirm = models.BooleanField(verbose_name="是否已确认", default=False)

    class Meta:
        db_table = "ops_ticket_user"
        verbose_name = '工单执行人信息'
        verbose_name_plural = verbose_name
