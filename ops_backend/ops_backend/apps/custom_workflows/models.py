# -*- coding:utf-8 -*-
from django.db import models
from models import BaseModel
from django.utils.translation import gettext_lazy as _
from common.Constant import CUSTOM_STATE
from django.db.models import Max


class Custom_Workflow(BaseModel):
    """
    自定义工作流
    """
    name = models.CharField(verbose_name="名称", max_length=50)
    description = models.TextField(verbose_name="描述", max_length=1024)
    is_active = models.BooleanField(verbose_name="激活状态", default=False)
    creator = models.ForeignKey("users.User", verbose_name="创建人", null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "ops_custom_workflow"
        verbose_name = "自定义工作流"
        verbose_name_plural = verbose_name


class Custom_Field(BaseModel):
    """自定义字段, 设定某个工作流有哪些自定义字段"""
    TYPE_CHOICE = (
        (1, "字符串"),
        (2, "整型"),
        (3, "浮点型"),
        (4, "布尔"),
        (5, "日期"),
        (6, "日期时间"),
        (7, "范围日期"),
        (8, "文本域"),
        (9, "单选框"),
        (10, "下拉列表"),
        (11, "外键"),
        (12, "多选框"),
        (13, "多选下拉"),
        (14, "多选外键"),
    )
    workflow = models.ForeignKey(Custom_Workflow, on_delete=models.CASCADE, verbose_name="工作流", related_name="field_list")
    field_type = models.IntegerField(choices=TYPE_CHOICE, default=1, verbose_name="字段类型")
    field_key = models.CharField(verbose_name="字段标识", max_length=50, help_text="字段类型请尽量特殊，避免与系统中关键字冲突")
    name = models.CharField(verbose_name="字段名称", max_length=50)
    order_id = models.IntegerField(verbose_name="排序", default=0)
    required = models.BooleanField(verbose_name="是否必填", default=False)
    displayed = models.BooleanField(verbose_name="是否展示", default=False)
    default_value = models.CharField(verbose_name="默认值", null=True, blank=True, max_length=100,
                                     help_text="前端展示时，可以将此内容作为表单中的该字段的默认值")
    field_placeholder = models.TextField(verbose_name="文本域模板", default="", null=True, blank=True,
                                         help_text="文本域类型字段前端显示时可以将此内容作为字段的placeholder")
    field_choice = models.CharField(verbose_name="radio、checkbox、select的选项", max_length=255, default="{}", null=True, blank=True,
                                    help_text="radio,checkbox,select,multiselect类型可供选择的选项，格式为json如:{'1':'中国', '2':'美国'},注意数字也需要引号")
    foreign_type = models.ForeignKey(
        to="contenttypes.ContentType",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("外键类型"),
        null=True
    )
    special_url = models.CharField(verbose_name="获取数据的url", max_length=100, null=True, blank=True, default=None,
                                   help_text="指定调用该url获取数据，<>中为其他字段的key，需要前端替换<>中的值，例如'/user/<test_id>'")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order_id"]
        db_table = "ops_custom_filed"
        verbose_name = "工作流自定义字段"
        verbose_name_plural = verbose_name
        unique_together = ("workflow", "field_key")


class Custom_State(BaseModel):
    """
    状态记录, 变量支持通过脚本获取
    """
    # 1.普通类型 0.初始状态(用于新建工单时,获取对应的字段必填及transition信息) 2.结束状态(此状态下的工单不得再处理，即没有对应的transition)
    STATE_CHOICE = (
        (0, "初始状态"),
        (1, "普通状态"),
        (2, "结束状态"),
    )
    PARTICIPANT_CHOICE = (
        (0, "无"),
        (1, "个人"),
        (2, "角色"),
        (3, "自定义字段用户"),
    )
    name = models.CharField(verbose_name="名称", max_length=50)
    workflow = models.ForeignKey(Custom_Workflow, on_delete=models.CASCADE, verbose_name="工作流",
                                 related_name="status_list")
    order_id = models.IntegerField(verbose_name="状态顺序", default=1)
    state_type = models.IntegerField(choices=STATE_CHOICE, default=0, verbose_name="状态类型")
    enable_retreat = models.BooleanField(verbose_name="允许撤回", default=False,
                                         help_text="开启后允许工单创建人在此状态直接撤回工单到初始状态")
    participant_type = models.IntegerField(choices=PARTICIPANT_CHOICE, default=0, verbose_name="参与者类型")
    participant = models.CharField(verbose_name="参与者", default="[]", null=True, blank=True, max_length=1000,
                                   help_text='可以为userid/多个userid(以,隔开)/角色id/多个角色id(以,隔开)')
    fields = models.ManyToManyField(Custom_Field, blank=True, verbose_name="可编辑字段", through="Status_Field")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["order_id"]
        db_table = "ops_custom_status"
        verbose_name = "工作流状态"
        verbose_name_plural = verbose_name
        unique_together = ("workflow", "name")

    def get_status_process(self):
        workflow = self.workflow
        if self.state_type != CUSTOM_STATE.TYPE.End:
            max_order = workflow.status_list.aggregate(Max('order_id'))['order_id__max']
            process = self.order_id / max_order * 100
            return int(process)
        return 100


class Status_Field(models.Model):
    state = models.ForeignKey(Custom_State, on_delete=models.CASCADE)
    field = models.ForeignKey(Custom_Field, on_delete=models.CASCADE)

    class Meta:
        db_table = "ops_custom_status_fields"
        verbose_name = "状态字段关联表"
        verbose_name_plural = verbose_name


class Custom_Transition(BaseModel):
    """
    工作流流转，定时器，条件(允许跳过)， 条件流转与定时器不可同时存在
    """
    TYPE_CHOICE = (
        (1, "保存"),
        (2, "完成"),
        (3, "移交"),
        (4, "驳回"),
        (5, "关闭"),
    )
    # 指定需要一个人处理还是全部人处理才进入下一步
    DISTRIBUTE_CHOICE = (
        (1, "只需要单个处理"),
        (2, "需要全部处理"),
    )
    name = models.CharField(verbose_name="流转名称", max_length=50)
    workflow = models.ForeignKey(Custom_Workflow, on_delete=models.CASCADE, verbose_name="工作流")
    source_state = models.ForeignKey(Custom_State, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name="source_state", verbose_name="源状态")
    dest_state = models.ForeignKey(Custom_State, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name="dest_state",
                                   verbose_name="目的状态")
    # attribute_type = models.IntegerField(choices=TYPE_CHOICE, default=1,
    #                                      verbose_name="属性类型")
    trans_type = models.IntegerField(choices=DISTRIBUTE_CHOICE, verbose_name='处理方式', default=1)
    alert_enable = models.BooleanField(verbose_name="点击弹窗提示", default=False)
    alert_text = models.CharField(verbose_name="弹窗内容", max_length=100, default="", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ops_custom_transition"
        verbose_name = "工作流流转"
        verbose_name_plural = verbose_name


class Custom_Trigger(models.Model):
    TYPE_CHOICE = (
        (1, "发送消息给后续人员"),
        (2, "自定义"),
    )
    transition = models.ForeignKey(Custom_Transition, on_delete=models.CASCADE, related_name="triggers")
    type = models.IntegerField(choices=TYPE_CHOICE, verbose_name="触发器类型", default=1)
    order = models.IntegerField(verbose_name="触发器顺序", default=1)

    class Meta:
        db_table = "ops_custom_trigger"
        verbose_name = "工作流流转触发器"
        verbose_name_plural = verbose_name
