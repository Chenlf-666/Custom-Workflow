from django.db import models


class Menu(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="菜单名")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="父菜单", related_name="leaves")
    order = models.IntegerField(null=True, blank=True, verbose_name="排序")
    index = models.CharField(max_length=50, null=True, blank=True, verbose_name="url索引")
    urls = models.CharField(max_length=1024, null=True, blank=True, verbose_name="包含url")
    workflow_id = models.IntegerField(null=True, blank=True, verbose_name="工作流id")

    class Meta:
        db_table = 'ops_menu'
        verbose_name = '菜单信息'
        verbose_name_plural = verbose_name
