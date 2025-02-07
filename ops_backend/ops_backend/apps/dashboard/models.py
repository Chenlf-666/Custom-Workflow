from django.db import models
from models import BaseModel


class ToDo_Task(BaseModel):
    TYPE_CHOICE = (
        (1, "Reset PassWord"),
        (2, "Check Ticket"),
    )
    type = models.IntegerField(choices=TYPE_CHOICE, verbose_name="任务类型", default=1)
    reference_id = models.BigIntegerField(verbose_name="关联对象ID", null=True, default=None)
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE)
    completed = models.BooleanField(verbose_name="是否完成", default=False)

    class Meta:
        db_table = "ops_todo_tasks"
        verbose_name = "个人任务"
        verbose_name_plural = verbose_name