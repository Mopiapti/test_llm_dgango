from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class ChatSession(models.Model):
    """Chat session between user and LLM."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat {self.id} - {self.user.username} - {self.title or 'No Title'}"


class ChatMessage(models.Model):
    """Individual messages in a chat session."""
    
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    
    # For SQL-related responses
    generated_sql = models.TextField(blank=True)
    sql_result = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update session timestamp
        self.session.updated_at = timezone.now()
        self.session.save(update_fields=['updated_at'])