# -*- coding:utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path(r'custom_workflows', views.WorkflowListCreateAPI.as_view()),
    path(r'custom_workflows/content_types', views.ContentTypeListAPI.as_view()),
    path(r'custom_workflows/<int:pk>', views.WorkflowDetailAPI.as_view()),
    path(r'custom_workflows/<int:pk>/active', views.WorkflowActiveAPI.as_view()),
    path(r'custom_workflows/<int:pk>/field', views.FieldListCreateAPI.as_view()),
    path(r'custom_workflows/<int:pk>/field/<int:field_id>', views.FieldDetailAPI.as_view()),
    path(r'custom_workflows/<int:pk>/field/<int:field_id>/relate_url', views.FieldRelateUrlAPI.as_view()),
    path(r'custom_workflows/<int:pk>/status', views.StatusListCreateAPI.as_view()),
    path(r'custom_workflows/<int:pk>/status/<int:status_id>', views.StatusDetailAPI.as_view()),
    path(r'custom_workflows/<int:pk>/init_status', views.InitialStatusAPI.as_view()),
    path(r'custom_workflows/<int:pk>/transition', views.TransitionListCreateAPI.as_view()),
    path(r'custom_workflows/<int:pk>/transition/<int:transition_id>', views.TransitionDetailAPI.as_view()),
]
