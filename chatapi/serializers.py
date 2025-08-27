# serializers.py
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'content', 'generated_sql', 'sql_result', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions."""
    messages_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages_count', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_messages_count(self, obj):
        """Get total number of messages in this session."""
        return obj.messages.count()
    
    def get_last_message(self, obj):
        """Get the most recent message content."""
        last_msg = obj.messages.first()
        if last_msg:
            return {
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'message_type': last_msg.message_type,
                'created_at': last_msg.created_at
            }
        return None


class ChatSessionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for chat sessions with messages."""
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateChatSerializer(serializers.ModelSerializer):
    """Serializer for creating new chat sessions."""
    
    class Meta:
        model = ChatSession
        fields = ['title']


class CreateMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""
    
    class Meta:
        model = ChatMessage
        fields = ['content']

# ============================================================================
# CHAT PROCESSING SERIALIZERS (SIMPLE)
# ============================================================================

class ChatProcessRequestSerializer(serializers.Serializer):
    """Simple serializer for chat processing requests."""
    chat_id = serializers.UUIDField(required=False, allow_null=True)
    message = serializers.CharField()


class ChatProcessResponseSerializer(serializers.Serializer):
    """Simple serializer for chat processing responses."""
    chat_id = serializers.UUIDField()
    answer = serializers.CharField()
    created_new_chat = serializers.BooleanField()