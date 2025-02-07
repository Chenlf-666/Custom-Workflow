# 消息相关功能
import os
import requests
import traceback
import logging
from datetime import datetime, date
from users.models import Message_Record

logger = logging.getLogger("Django")


class SendWeiXinWork:
    PwdExpire = 1
    CheckWorkflow = 2
    mail_suffix_list = ["@testtest.com"]
    mail_type_list = [2, 1]

    def __init__(self):
        self.CORP_ID = "xxx"  # 企业号的标识
        self.SECRET = "xxx"  # 管理组凭证密钥
        self.AGENT_ID = 10001  # 应用ID
        self.DEPARTMENT_ID = 1
        self.TOKEN = self.GetTokenFromServer()

    def CheckDuplication(self, msg_type, content, owner):
        # 检查是否重复
        if Message_Record.objects.filter(
            type=msg_type,
            content=content,
            receiver=owner,
            status=1
        ):
            return True
        return False

    def GetTokenFromServer(self):
        """获取access_token"""
        Url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        Data = {
            "corpid": self.CORP_ID,
            "corpsecret": self.SECRET
        }
        r = requests.get(url=Url, params=Data, verify=False)
        result = r.json()
        if result.get("errcode"):
            logger.error("获取企业微信认证信息失败")
            return False
        else:
            Token = r.json()['access_token']
            return Token

    def GetWXUser(self, user):
        """获取对应企业微信的用户名"""
        Url = "https://qyapi.weixin.qq.com/cgi-bin/user/get_userid_by_email?access_token={}".format(self.TOKEN)
        data_list = [{"email": user.username + domain, "email_type": num} for domain in self.mail_suffix_list for num in self.mail_type_list]
        for data in data_list:
            r = requests.post(url=Url, json=data)
            result = r.json()
            if not result.get("errcode"):
                return result.get("userid", None)

        # 如果用邮箱无法获取，尝试用旧方法
        Url2 = "https://qyapi.weixin.qq.com/cgi-bin/user/simplelist?access_token={}&department_id={}&fetch_child=1".format(
            self.TOKEN, self.DEPARTMENT_ID)
        r = requests.get(url=Url2)
        result = r.json()
        userList = result.get("userlist", [])
        for userInfo in userList:
            if userInfo.get("name") == user.fullname():
                return userInfo.get("userid")
        return None

    def SendPwdExpireMessage(self, user, days):
        msg = "您的密码还剩{}天过期，请尽快修改".format(days)
        try:
            userId = self.GetWXUser(user)
            Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(self.TOKEN)

            Data = {
                "touser": userId,
                "msgtype": "textcard",
                "agentid": self.AGENT_ID,
                "textcard": {
                    "title": "密码过期提示",
                    "description": "<div class=\"gray\">{}</div> <div class=\"normal\">{}</div>".format(
                        datetime.now().strftime("%Y年%m月%d日"),
                        msg
                    ),
                    "url": "https://{}/#/profile".format(os.environ.get("domain", "localhost:5173")),
                    "btntxt": "点击跳转"
                },
                "enable_duplicate_check": 1,
                "duplicate_check_interval": 600
            }

            r = requests.post(url=Url, json=Data)
            result = r.json()
            if not result.get("errcode"):
                Message_Record.objects.create(
                    receiver=user,
                    receiver_name=user.fullname(),
                    content=msg,
                    type=self.PwdExpire
                )
            else:
                Message_Record.objects.create(
                    receiver=user,
                    receiver_name=user.fullname(),
                    content=result.get("errmsg"),
                    status=2,
                    type=self.PwdExpire
                )
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            Message_Record.objects.create(
                receiver=user,
                receiver_name=user.fullname(),
                content=msg,
                status=2,
                type=self.PwdExpire
            )

    def SendCustomMessage(self, user, content):
        try:
            userId = self.GetWXUser(user)
            Url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(self.TOKEN)

            Data = {
                "touser": userId,
                "msgtype": "textcard",
                "agentid": self.AGENT_ID,
                "textcard": {
                    "title": "任务通知",
                    "description": "<div class=\"gray\">{}</div> <div class=\"normal\">{}</div>".format(
                        datetime.now().strftime("%Y年%m月%d日"),
                        content
                    ),
                    "url": "https://{}".format(os.environ.get("domain", "localhost:5173")),
                    "btntxt": "点击跳转"
                },
                "enable_duplicate_check": 0,
                "duplicate_check_interval": 600
            }

            r = requests.post(url=Url, json=Data)
            result = r.json()
            if not result.get("errcode"):
                Message_Record.objects.create(
                    receiver=user,
                    receiver_name=user.fullname(),
                    content=content,
                    type=self.CheckWorkflow
                )
            else:
                Message_Record.objects.create(
                    receiver=user,
                    receiver_name=user.fullname(),
                    content=result.get("errmsg"),
                    status=2,
                    type=self.CheckWorkflow
                )
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            Message_Record.objects.create(
                receiver=user,
                receiver_name=user.fullname(),
                content=content,
                status=2,
                type=self.CheckWorkflow
            )
