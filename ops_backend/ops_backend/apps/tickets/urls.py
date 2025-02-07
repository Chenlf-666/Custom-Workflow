# -*- coding:utf-8 -*-
from django.urls import path
from . import views


urlpatterns = [
    path(r'tickets', views.TicketListCreateAPI.as_view()),
    path(r'tickets/<int:pk>', views.TicketDetailAPI.as_view()),
    path(r'tickets/<int:pk>/log', views.TicketLogAPI.as_view()),
    path(r'tickets/<int:pk>/current_fields', views.TicketCurrentStateFieldsAPI.as_view()),
    path(r'tickets/<int:pk>/transition', views.TicketHandleAPI.as_view()),
    path(r'tickets/<int:pk>/assign', views.TicketAssignAPI.as_view()),
    path(r'tickets/<int:pk>/retreat', views.TicketRetreatAPI.as_view()),
    path(r'tickets/<int:pk>/field/<int:field_id>/relate_url', views.TicketFieldRelateUrlAPI.as_view()),
]
