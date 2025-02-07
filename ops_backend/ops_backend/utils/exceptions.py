import logging, traceback
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from enum import Enum
from deprecated.sphinx import deprecated

# 获取在配置文件中定义的 logger，用来记录日志
logger = logging.getLogger('django')

# 将仅针对由引发的异常生成的响应调用异常处理程序。它不会用于视图直接返回的任何响应
def custom_exception_handler(exc: Exception, context):
    logger.error(traceback.format_exc())
    
    r: Response = drf_exception_handler(exc, context)

    if r is not None:    # DRF 处理
        response = Response({}, r.status_code)
        response.data = { 'status_code': r.status_code,                         'message': str(exc) if str(exc) else r.status_text }
    else:                # 自定义处理
        response = Response({}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response.data = { 'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR, 'message': str(exc) if str(exc) else '服务器错误' }

    return response



@deprecated
class StatusEnum(Enum):
    """状态码枚举类"""

    # OK                     = (20000, '成功')
    
    CLIENT_ERR             = (40000, '请求错误')
    USERNAME_ERR           = (40001, '用户名错误')
    PWD_ERR                = (40002, '密码错误')
    CPWD_ERR               = (40003, '密码不一致')
    MOBILE_ERR             = (40004, '手机号错误')
    SESSION_ERR            = (40005, '用户未登录')
    PARAMETER_ERR          = (40007, '参数错误')
    FIELD_ERR              = (40007, '字段不存在')

    SERVER_ERR             = (50000, '服务器内部错误')
    ROW_NOT_EXIST_ERR      = (50001, '记录不存在')

    @property
    def code(self) -> int:
        """获取状态码"""
        return self.value[0]

    @property
    def message(self) -> str:
        """获取状态码信息"""
        return self.value[1]

class CommonException(Exception):
    """公共异常类"""

    def __init__(self, status_enum: StatusEnum, custom_message: str = None) -> None:
        """_summary_

        Args:
            status_enum (StatusEnum): StatusEnum
            custom_message (str): 自定义提示，会覆盖 StatusEnum 的 Message。
        """
        super().__init__()
        self.status = status_enum
        self.custom_message = custom_message

    @property
    def response(self) -> dict:
        """获取响应信息"""
        return {
            'code': self.status.code,
            'message': self.custom_message if self.custom_message is not None else self.status.message
        }

class APIException(CommonException):
    """API 异常类"""
    pass
