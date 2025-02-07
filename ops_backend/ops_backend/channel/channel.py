from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from . import routings

application = AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            routings.urlpatterns
        )
    )