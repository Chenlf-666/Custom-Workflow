# -*- coding:utf-8 -*-


class MENU:
    DashBoard = "系统首页"
    ManageCenter = "管理中心"
    SystemConfig = "系统配置"
    UserManage = "用户管理"
    PermissionManage = "权限管理"
    LogManage = "日志管理"
    CustomWorkflowManage = "工作流管理"
    ApprovalProcess = "审批流程"
    TicketManage = "工单管理"

    TREE = {
        DashBoard: {
            "order": 1,
            "index": "/dashboard"
        },
        ApprovalProcess: {
            "order": 2,
            "leaf": {
            }
        },
        ManageCenter: {
            "order": 3,
            "leaf": {
                TicketManage: {
                    "order": 1,
                    "index": "/worksheet",
                    "urls": "/tickets.*"
                },
                UserManage: {
                    "order": 2,
                    "index": "/users",
                    "urls": "/auth/reset-user-password"
                },
            }
        },
        SystemConfig: {
            "order": 4,
            "leaf": {
                UserManage: {
                    "order": 1,
                    "index": "/users",
                    "urls": "/auth/reset-user-password"
                },
                PermissionManage: {
                    "order": 2,
                    "index": "/permission",
                    "urls": "/auth/groups,/auth/groups/<pk>"
                },
                LogManage: {
                    "order": 3,
                    "index": "/log",
                },
                CustomWorkflowManage: {
                    "order": 4,
                    "index": "/customWorkflows",
                    "urls": "/custom_workflows.*"
                }
            }
        }
    }


class TODO_TYPE:
    ResetPassWord = 1   # 重置密码
    CheckTicket = 2     # 确认工单任务


class CUSTOM_FIELD_TYPE:
    String = 1
    Int = 2
    Float = 3
    Boolean = 4
    Date = 5
    Time = 6
    RangeTime = 7
    Text = 8
    Radio = 9
    Select = 10
    Foreign = 11
    CheckBox = 12
    MultiSelect = 13
    MultiForeign = 14


class CUSTOM_STATE:
    class TYPE:
        Init = 0
        Normal = 1
        End = 2

    class PARTICIPANT_TYPE:
        Empty = 0
        User = 1
        Role = 2
        Field = 3


class CUSTOM_TRANSITION:
    class Type:
        Save = 1
        Complete = 2
        Assign = 3
        Refuse = 4
        Close = 5

    class TRANS_TYPE:
        Single = 1
        All = 2
