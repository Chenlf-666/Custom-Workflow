# -*- coding:utf-8 -*-
import ast
import json
import logging

from common.Constant import TODO_TYPE, CUSTOM_STATE, CUSTOM_FIELD_TYPE
from custom_workflows.models import Custom_Field
from dashboard.models import ToDo_Task
from tickets.models import Ticket
from users.models import User

logger = logging.getLogger("Django")


def check_todo_list(obj, reference_id, task_type):
    if task_type == TODO_TYPE.ResetPassWord:
        ToDo_Task.objects.filter(owner=obj, type=task_type).update(completed=True)
    elif task_type == TODO_TYPE.CheckTicket:
        ticket = Ticket.objects.get(id=reference_id)
        if ticket.status.state_type == CUSTOM_STATE.TYPE.End:
            # 已完成的任务，全部更新为true
            ToDo_Task.objects.filter(reference_id=reference_id, type=task_type).update(completed=True)
            return
        if obj != ticket.status:
            # 说明进入了下一状态，上一状态的任务需要清除
            for old_operator in ticket.users.filter(status=obj):
                old_user = old_operator.operator
                ToDo_Task.objects.filter(owner=old_user, reference_id=reference_id, type=task_type).update(completed=True)
        user_list = []
        for ticket_operator in ticket.users.filter(status=ticket.status):
            user = ticket_operator.operator
            user_list.append(user)
            if not ticket_operator.is_confirm:
                ToDo_Task.objects.update_or_create(
                    defaults={
                        "completed": False
                    },
                    owner=user,
                    reference_id=ticket.id,
                    type=task_type
                )
            if not ticket.users.filter(
                    operator=user,
                    is_confirm=False,
                    status=ticket.status
            ):
                ToDo_Task.objects.filter(owner=user, reference_id=reference_id, type=task_type).update(completed=True)
        ToDo_Task.objects.filter(reference_id=reference_id, type=task_type).exclude(owner__in=user_list).delete()


def get_displayed_value(custom_field: Custom_Field, field_value):
    if custom_field.field_type in [CUSTOM_FIELD_TYPE.Foreign, CUSTOM_FIELD_TYPE.MultiForeign]:
        if custom_field.field_type == CUSTOM_FIELD_TYPE.Foreign:
            id_list = [field_value]
        else:
            id_list = json.loads(field_value)
        foreign_type = custom_field.foreign_type
        model_class = foreign_type.model_class()
        if model_class == User:
            name_list = [item.fullname() for item in model_class.objects.filter(id__in=id_list)]
        else:
            name_list = [item.name for item in model_class.objects.filter(id__in=id_list)]
        return "、".join(name_list)
    elif custom_field.field_type in [CUSTOM_FIELD_TYPE.Radio, CUSTOM_FIELD_TYPE.Select,
                                     CUSTOM_FIELD_TYPE.CheckBox,
                                     CUSTOM_FIELD_TYPE.MultiSelect]:
        return get_selected_value(field_value, custom_field.field_choice)
    elif custom_field.field_type == CUSTOM_FIELD_TYPE.RangeTime:
        return " ~ ".join(ast.literal_eval(field_value))
    else:
        return field_value


def get_selected_value(keys, choice_list):
    if choice_list:
        try:
            key_list = ast.literal_eval(keys)
            if not isinstance(key_list, list):
                key_list = [key_list]
        except ValueError:
            key_list = [str(keys)]
        value_list = []
        for key in key_list:
            value = list(filter(lambda x: str(x['key']) == str(key), ast.literal_eval(choice_list)))[0]['value']
            value_list.append(str(value))
        return "、".join(value_list)
    return keys
