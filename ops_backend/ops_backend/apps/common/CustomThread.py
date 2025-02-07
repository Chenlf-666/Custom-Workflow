import threading
from common.Message import SendWeiXinWork


class thread_send_msg_to_user_group(threading.Thread):
    subject = "Workflow"

    def __init__(self, users, groups, ticket):
        super().__init__()
        self.users = users
        self.groups = groups
        self.ticket = ticket

    def run(self) -> None:
        connect = SendWeiXinWork()
        content = "有《{}》任务需要您处理，请确认".format(self.ticket.name)
        if self.users:
            for user in self.users:
                connect.SendCustomMessage(user, content)
        if self.groups:
            for group in self.groups:
                for user in group.user_set.filter(is_active=True).exclude(last_login__isnull=True):
                    connect.SendCustomMessage(user, content)
