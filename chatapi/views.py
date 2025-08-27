import logging
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer,
    ChatSessionDetailSerializer,
    CreateChatSerializer,
    CreateMessageSerializer,
    ChatMessageSerializer,
    ChatProcessRequestSerializer,
)
from .services.llm_langgraph import SQLQuerySystem

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)


class ProcessChatMessageView(generics.GenericAPIView):
    """Main endpoint for processing chat messages through LLM system."""
    
    serializer_class = ChatProcessRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm_system = SQLQuerySystem()
    
    def post(self, request):
        """Process chat message through LLM system with conversation history."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        chat_id = serializer.validated_data.get('chat_id')
        message_content = serializer.validated_data['message']
        user = request.user
        
        try:
            # Step 1: Get or create chat session
            chat_session, created_new_chat = self._get_or_create_chat_session(chat_id, user)
            
            # Step 2: Get conversation history if existing chat
            conversation_history = self._get_conversation_history(chat_session)
            
            # Step 3: Save user message
            user_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='user',
                content=message_content
            )
            
            # Step 4: Process through LLM system with history
            llm_result = self._process_with_llm_and_history(message_content, conversation_history)
            
            # Step 5: Save assistant response
            assistant_message = ChatMessage.objects.create(
                session=chat_session,
                message_type='assistant',
                content=llm_result.get('answer', 'No response generated'),
                generated_sql=llm_result.get('query', ''),
                sql_result=str(llm_result.get('sql_result', ''))
            )
            
            # Step 6: Generate title for new chats
            if created_new_chat and not chat_session.title:
                self._generate_chat_title(chat_session, message_content)
            
            return Response({
                'chat_id': chat_session.id,
                'answer': assistant_message.content,
                'created_new_chat': created_new_chat
            })
            
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return Response({
                'error': f'Error processing message: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_or_create_chat_session(self, chat_id, user):
        """Get existing chat session or create new one."""
        if chat_id:
            try:
                chat_session = ChatSession.objects.get(id=chat_id, user=user)
                return chat_session, False
            except ChatSession.DoesNotExist:
                raise ValueError('Chat session not found')
        else:
            chat_session = ChatSession.objects.create(user=user)
            return chat_session, True
    
    def _get_conversation_history(self, chat_session):
        """Get formatted conversation history for LLM context."""
        # Get all messages for this session, ordered chronologically (oldest first)
        messages = chat_session.messages.all().order_by('created_at')
        
        conversation_history = []
        for message in messages:
            # Format message for LLM context
            if message.message_type == 'user':
                role = "Human"
            else:  # assistant
                role = "Assistant"
            
            conversation_history.append({
                'role': role,
                'content': message.content
            })
        
        logger.info(f"Retrieved {len(conversation_history)} messages for conversation history")
        return conversation_history
    
    def _process_with_llm_and_history(self, message_content, conversation_history):
        """Process message through LLM system with conversation history."""
        logger.info(f"Processing message with {len(conversation_history)} historical messages")
        
        try:
            # Format the message with conversation history
            formatted_input = self._format_message_with_history(message_content, conversation_history)
            
            # Process through your LLM system
            result = self.llm_system.query(formatted_input, stream=False)
            return result
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return {
                'question': message_content,
                'query': 'SELECT 1;',
                'sql_result': 'Error processing query',
                'answer': 'I apologize, but I encountered an error while processing your request.'
            }
    
    def _format_message_with_history(self, current_message, conversation_history):
        """Format current message with conversation history for LLM context."""
        if not conversation_history:
            # No history, just return current message
            return current_message
        
        # Build context with conversation history
        context_parts = ["Previous conversation context:"]
        
        # Add conversation history (limit to last 10 exchanges to avoid token limits)
        recent_history = conversation_history[-20:]  # Last 20 messages (10 exchanges)
        
        for msg in recent_history:
            context_parts.append(f"{msg['role']}: {msg['content']}")
        
        # Add current message
        context_parts.extend([
            "",
            "Current question:",
            current_message
        ])
        
        formatted_input = "\n".join(context_parts)
        
        logger.debug(f"Formatted input with history: {formatted_input[:200]}...")
        return formatted_input
    
    def _generate_chat_title(self, chat_session, first_message):
        """Generate a title for new chat sessions."""
        title = first_message[:50] + "..." if len(first_message) > 50 else first_message
        chat_session.title = title
        chat_session.save(update_fields=['title'])


@extend_schema(
    summary="List user's chat sessions",
    description="Retrieve all chat sessions for the authenticated user.",
    responses={200: ChatSessionSerializer(many=True)},
    tags=['Chat Sessions']
)
class ChatSessionListView(generics.ListAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


@extend_schema(
    summary="Get chat session details",
    description="Retrieve a specific chat session with all its messages.",
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='UUID of the chat session'
        )
    ],
    responses={200: ChatSessionDetailSerializer, 404: {'description': 'Not Found'}},
    tags=['Chat Sessions']
)
class ChatSessionDetailView(generics.RetrieveAPIView):
    serializer_class = ChatSessionDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).prefetch_related('messages')


@extend_schema(
    summary="Create new chat session",
    description="Create a new chat session.",
    request=CreateChatSerializer,
    responses={201: ChatSessionSerializer},
    examples=[
        OpenApiExample(
            'Create chat with title',
            request_only=True,
            value={'title': 'Product Research Chat'}
        )
    ],
    tags=['Chat Sessions']
)
class CreateChatView(generics.CreateAPIView):
    serializer_class = CreateChatSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_session = serializer.save(user=request.user)
        return Response(ChatSessionSerializer(chat_session).data, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Add message to chat",
    description="Add a new message to an existing chat session.",
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='UUID of the chat session'
        )
    ],
    request=CreateMessageSerializer,
    responses={201: ChatMessageSerializer},
    tags=['Messages']
)
class AddMessageToChatView(generics.CreateAPIView):
    serializer_class = CreateMessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        chat_session = get_object_or_404(
            ChatSession,
            id=self.kwargs['id'],
            user=request.user
        )

        message = serializer.save(session=chat_session, message_type='user')
        return Response({
            'message': 'Message added successfully',
            'data': ChatMessageSerializer(message).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Update chat title",
    description="Update the title of an existing chat session.",
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='UUID of the chat session'
        )
    ],
    request=CreateChatSerializer,
    responses={200: ChatSessionSerializer},
    tags=['Chat Sessions']
)
class UpdateChatTitleView(generics.UpdateAPIView):
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


@extend_schema(
    summary="Delete chat session",
    description="Delete a chat session and all its messages.",
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='UUID of the chat session'
        )
    ],
    responses={200: {'description': 'Chat deleted successfully'}},
    tags=['Chat Sessions']
)
class DeleteChatView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Chat session deleted successfully'}, status=status.HTTP_200_OK)
