from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.middleware import get_user
from django.utils.functional import SimpleLazyObject

from auditlog.context import set_actor
from auditlog.middleware import AuditlogMiddleware as _AuditlogMiddleware


class JWTAuthenticationMiddleware(AuthenticationMiddleware):

    def process_request(self, request):
        super().process_request(request)

        request.user = SimpleLazyObject(
            lambda: self.__class__.get_jwt_user(request))

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user
        jwt_authentication = JWTAuthentication()
        if jwt_authentication.get_header(request):
            try:
                user, jwt = jwt_authentication.authenticate(request)
            except Exception as e:
                try:
                    session_auth = SessionAuthentication()
                    user, jwt = session_auth.authenticate(request)
                except Exception as e:
                    try:
                        basic_auth = BasicAuthentication()
                        user, jwt = basic_auth.authenticate(request)
                    except Exception as e:
                        return user
        return user


class AuditlogMiddleware(_AuditlogMiddleware):
    def __call__(self, request):
        remote_addr = self._get_remote_addr(request)
        user = SimpleLazyObject(lambda: getattr(request, "user", None))
        context = set_actor(actor=user, remote_addr=remote_addr)

        with context:
            return self.get_response(request)