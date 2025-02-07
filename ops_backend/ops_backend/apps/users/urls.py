from django.urls import path
from . import views

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
urlpatterns = [
    # path('login/', obtain_jwt_token),
    path(r'login', views.UserLoginView.as_view(), name='login'),
    path(r'verify', TokenVerifyView.as_view(), name='token_verify'),  # 这是只是校验token有效性
    path(r'refresh', TokenRefreshView.as_view(), name='token_refresh'),  # 校验并生成新的token
    path(r'change-password', views.ChangeUserPasswordView.as_view(), name='change_password'),
    path(r'reset-user-password', views.ResetUserPasswordView.as_view(), name='reset_user_password'),

    # 获取用户详情
    path(r'profile', views.UserProfileView.as_view(), name='profile'),
    path(r'users', views.UserListView.as_view(), name='user-list'),
    path(r'users/<int:pk>', views.UserDetailView.as_view(), name='user-detail'),
    path(r'auditlog', views.LogEntryList.as_view()),
    path(r'auditlog/<int:pk>', views.LogEntryDetail.as_view()),

    path(r'permissions', views.PermissionListView.as_view()),
    path(r'groups', views.GroupListCreateView.as_view()),
    path(r'groups/<int:pk>', views.GroupDetailView.as_view()),
]
