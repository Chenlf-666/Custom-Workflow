# -*- coding:utf-8 -*-
import json
import traceback
import logging
from tickets.models import *
from custom_workflows.models import *
from common.CustomThread import thread_send_msg_to_user_group
from common.Constant import CUSTOM_STATE

logger = logging.getLogger("Django")

# 处理触发器
def handle_trigger(ticket: Ticket, transition: Custom_Transition):
    workflow = ticket.workflow
    dest_state = transition.dest_state
    for trigger in transition.triggers.order_by("type"):
        if trigger.type == 1:
            # 发送消息
            participant_type = dest_state.participant_type
            if participant_type != CUSTOM_STATE.PARTICIPANT_TYPE.Empty:
                if dest_state.participant and dest_state.participant != "[]":
                    try:
                        participant_ids = json.loads(dest_state.participant)
                        if isinstance(participant_ids, int):
                            participant_ids = [participant_ids]
                        if participant_type == CUSTOM_STATE.PARTICIPANT_TYPE.Role:
                            groups = Ops_Group.objects.filter(id__in=participant_ids)
                            t = thread_send_msg_to_user_group(None, groups, ticket)
                            t.start()
                        else:
                            users = User.objects.filter(ticket_operator__ticket=ticket, ticket_operator__status=dest_state).distinct()
                            t = thread_send_msg_to_user_group(users, None, ticket)
                            t.start()
                    except json.decoder.JSONDecodeError:
                        logger.error(traceback.format_exc())
                    except Custom_Field.DoesNotExist:
                        logger.error("custom_field not found")
                    except Ticket_Field.DoesNotExist:
                        logger.error("ticket_field not found")

        elif trigger.type == 2:
            pass
