class Platforms:
    """平台类型"""

    WINDOWS: str      = "Windows"
    UNIX: str         = "Linux"
    
class Deployments:
    """部署方式"""

    COMPOSE: str      = "compose"
    K8S: str          = "k8s"
    LOCAL: str        = "local"