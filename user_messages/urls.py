from django.urls import path
from . import views
from user_messages.models import Message


urlpatterns = [
    path('messages/', views.messages_list_create, name='messages-list-create'),
]
