# Create your views here.
from rest_framework import status, filters
from rest_framework.generics import RetrieveAPIView, ListAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.response import Response

from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import *
from .filter import *
from auditlog.models import LogEntry, ContentType
from common.permissions import MenuPermissionRequired
from permissions import IsAdminUserOrIsAuthenticatedReadOnly


class UserLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        instance = serializer.user
        content_type = ContentType.objects.get_for_model(User)
        LogEntry.objects.create(
            content_type=content_type,
            object_pk=instance.pk,
            object_id=instance.id,
            object_repr=str(instance),
            action=LogEntry.Action.ACCESS,
            changes="",
            actor=instance,
            remote_addr=request.META.get("REMOTE_ADDR", "")
        )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# GET /users/profile
class UserProfileView(RetrieveAPIView):
    """用户详细信息展示"""
    serializer_class = UserProfileSerializer
    # queryset = User.objects.all()
    permission_classes = [IsAuthenticated]  # 指定权限,只有通过认证的用户才能访问当前视图

    def get_object(self):
        """重写此方法返回 要展示的用户模型对象"""
        # self.request.user.fullname = self.request.user.last_name + self.request.user.first_name
        return self.request.user


# 获取所有用户
class UserListView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=1).order_by('username')
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']


class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put"]

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs.get("pk"))


class ChangeUserPasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        user = request.user
        if old_password != user.password:
            return Response(data={"message": "密码错误"}, status=status.HTTP_403_FORBIDDEN)
        user.password = new_password
        user.save()
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


class ResetUserPasswordView(UpdateAPIView):
    permission_classes = [MenuPermissionRequired]
    serializer_class = UserSerializer

    def post(self, request):
        username = request.data.get('username')
        user = User.objects.get(username=username)
        new_password = request.data.get('new_password')
        user.password = new_password
        user.save()
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


class LogEntryList(ListAPIView):
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AuditLogFilter


    def get_queryset(self):
        user = self.request.user

        queryset = LogEntry.objects.filter(actor__isnull=False)

        if user.is_superuser:
            queryset = queryset.order_by("-id")
        else:
            queryset = queryset.filter(actor=user).order_by("-id")
        return queryset


class LogEntryDetail(RetrieveAPIView):
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AuditLogFilter

    def get_queryset(self):
        return LogEntry.objects.filter(id=self.kwargs.get("pk"))


class PermissionListView(ListAPIView):
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    queryset = Permission.objects.all().order_by("content_type")

    def test(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        result = serializer.data
        permissions_by_content_type = {}
        # 将权限按 content_type 分组
        for permission_info in result:
            content_type_id = permission_info.pop("content_type")
            content_type = ContentType.objects.get(id=content_type_id)
            if content_type.name not in permissions_by_content_type:
                try:
                    ContentType.objects.get_for_model(content_type.model_class())
                except AttributeError:
                    pass
                else:
                    permissions_by_content_type[content_type.name] = [permission_info]
            else:
                permissions_by_content_type[content_type.name].append(permission_info)
        return Response(permissions_by_content_type)


class GroupListCreateView(ListCreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUserOrIsAuthenticatedReadOnly]
    queryset = Ops_Group.objects.all().order_by("-update_time")
    filterset_class = GroupFilter


class GroupDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GroupDetailSerializer
    permission_classes = [IsAdminUserOrIsAuthenticatedReadOnly]
    http_method_names = ["get", "put", "delete"]

    def get_queryset(self):
        return Ops_Group.objects.filter(id=self.kwargs.get("pk"))

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user_set.all():
            return Response(data={"message": "组内存在用户，无法删除"}, status=status.HTTP_403_FORBIDDEN)
        return self.destroy(request, *args, **kwargs)
