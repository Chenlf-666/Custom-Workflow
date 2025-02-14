# Generated by Django 4.1.3 on 2025-01-23 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('name', models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='标题')),
            ],
            options={
                'verbose_name': '工单记录',
                'verbose_name_plural': '工单记录',
                'db_table': 'ops_tickets',
            },
        ),
        migrations.CreateModel(
            name='Ticket_Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('field_value', models.TextField(blank=True, default='', verbose_name='字段值')),
            ],
            options={
                'verbose_name': '工单自定义字段值',
                'verbose_name_plural': '工单自定义字段值',
                'db_table': 'ops_ticket_field',
            },
        ),
        migrations.CreateModel(
            name='Ticket_Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('suggestion', models.CharField(blank=True, max_length=140, null=True, verbose_name='审批意见')),
                ('participant', models.CharField(blank=True, default='', max_length=50, verbose_name='处理人')),
            ],
            options={
                'verbose_name': '工单流转日志',
                'verbose_name_plural': '工单流转日志',
                'db_table': 'ops_ticket_log',
            },
        ),
        migrations.CreateModel(
            name='Ticket_Operator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('is_confirm', models.BooleanField(default=False, verbose_name='是否已确认')),
            ],
            options={
                'verbose_name': '工单执行人信息',
                'verbose_name_plural': '工单执行人信息',
                'db_table': 'ops_ticket_user',
            },
        ),
    ]
