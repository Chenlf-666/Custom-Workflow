# -*- coding:utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path(r'dashboard/daily-login', views.StatByLoginAPI.as_view()),
    path(r'dashboard/mytasks', views.ToDoTaskListAPI.as_view()),
]
