from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    path('chat/process/', views.ProcessChatMessageView.as_view(), name='chat-process'),  # main endpoint
    path('chats/', views.ChatSessionListView.as_view(), name='chat-list'),
    path('chats/create/', views.CreateChatView.as_view(), name='chat-create'),
    path('chats/<uuid:id>/', views.ChatSessionDetailView.as_view(), name='chat-detail'),
    path('chats/<uuid:id>/messages/', views.AddMessageToChatView.as_view(), name='chat-add-message'),
    path('chats/<uuid:id>/update/', views.UpdateChatTitleView.as_view(), name='chat-update'),
    path('chats/<uuid:id>/delete/', views.DeleteChatView.as_view(), name='chat-delete'),
]