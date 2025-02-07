# -*- coding:utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path(r'menu/tree', views.MenuTreeView.as_view()),
    path(r'menu/index', views.MenuIndexView.as_view()),
    path(r'menu', views.MenuListCreateView.as_view()),
    path(r'menu/<int:pk>', views.MenuOperateView.as_view()),
]
