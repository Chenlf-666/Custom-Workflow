from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from models import BaseModel


# Create your models here.
# //User模型，继承Django认证系统的用户模型类，添加手机号码和用户头像两个字段

class User(AbstractUser):
    mobile = models.CharField(max_length=15, unique=False, verbose_name='手机号码')
    reset_pwd_stamp = models.BigIntegerField(verbose_name='重置密码时间戳', null=True, blank=True)

    def fullname(self):
        if self.last_name:
            return '%s%s' % (self.last_name, self.first_name)
        return self.username

    fullname.short_description = '全名'

    def role(self):
        if (self.is_superuser):
            return "超级管理员"
        elif (self.is_staff):
            return "管理员"
        else:
            return "普通用户"

    role.short_description = '角色'

    # 数据库信息
    class Meta:
        # 表名
        db_table = 'ops_users'
        # 详细名称
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True


class Ops_Group(Group, BaseModel):
    desc = models.CharField(max_length=512, verbose_name="描述", null=True, blank=True)
    menu_permissions = models.ManyToManyField("menu.Menu", blank=True, verbose_name="菜单授权")

    class Meta:
        db_table = 'ops_groups'
        verbose_name = '组信息'
        verbose_name_plural = verbose_name


class Message_Record(BaseModel):
    TYPE_CHOICE = (
        (1, "PwdExpire"),
        (2, "CheckTicket")
    )
    STATUS_CHOICE = (
        (1, "Success"),
        (2, "Failed"),
        (3, "UnSend"),
    )
    type = models.IntegerField(choices=TYPE_CHOICE, verbose_name="消息类型", default=1)
    receiver = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    receiver_name = models.CharField(max_length=100, verbose_name='接收者', null=True, blank=True)
    content = models.CharField(max_length=512, verbose_name="消息内容", null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICE, verbose_name="消息状态", default=1)

    class Meta:
        db_table = "ops_message_record"
        verbose_name = "消息记录"
        verbose_name_plural = verbose_name
