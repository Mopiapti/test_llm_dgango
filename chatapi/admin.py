from django.contrib import admin
from .models import ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):
    """Inline admin for chat messages within a session."""
    model = ChatMessage
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('message_type', 'content', 'generated_sql', 'sql_result', 'created_at')
    
    def get_queryset(self, request):
        """Order messages chronologically within the session."""
        return super().get_queryset(request).order_by('created_at')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin configuration for ChatSession model."""
    
    list_display = ('id', 'user', 'title', 'message_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'user')
    search_fields = ('title', 'user__username', 'user__email', 'id')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Session Info', {
            'fields': ('id', 'user', 'title')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        """Display the number of messages in the session."""
        return obj.messages.count()
    message_count.short_description = 'Messages'
    message_count.admin_order_field = 'messages__count'
    
    def get_queryset(self, request):
        """Optimize queries by prefetching related data."""
        return super().get_queryset(request).select_related('user').prefetch_related('messages')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin configuration for ChatMessage model."""
    
    list_display = ('id', 'session_title', 'user', 'message_type', 'content_preview', 'has_sql', 'created_at')
    list_filter = ('message_type', 'created_at', 'session__user')
    search_fields = ('content', 'session__title', 'session__user__username', 'generated_sql')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Message Info', {
            'fields': ('session', 'message_type', 'content')
        }),
        ('SQL Data', {
            'fields': ('generated_sql', 'sql_result'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def session_title(self, obj):
        """Display session title or fallback."""
        return obj.session.title or f"Session {str(obj.session.id)[:8]}..."
    session_title.short_description = 'Session'
    session_title.admin_order_field = 'session__title'
    
    def user(self, obj):
        """Display the user who owns the session."""
        return obj.session.user.username
    user.short_description = 'User'
    user.admin_order_field = 'session__user__username'
    
    def content_preview(self, obj):
        """Show a preview of the message content."""
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def has_sql(self, obj):
        """Indicate if the message has SQL data."""
        return bool(obj.generated_sql or obj.sql_result)
    has_sql.short_description = 'Has SQL'
    has_sql.boolean = True
    
    def get_queryset(self, request):
        """Optimize queries by prefetching related data."""
        return super().get_queryset(request).select_related('session__user')