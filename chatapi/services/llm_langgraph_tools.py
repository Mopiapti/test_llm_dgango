from typing import Dict, Any, List, Union, Optional
from typing_extensions import TypedDict, Annotated
from abc import ABC, abstractmethod

from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, StateGraph
from django.conf import settings
from constance import config
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langgraph.runtime import Runtime

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class State(TypedDict):
    messages: Annotated[list, add_messages]


class ContextSchema(TypedDict):
    system_prompt: SystemMessage


class MessageProcessor(ABC):
    """Abstract base class for message processors."""
    
    @abstractmethod
    def process_messages(self, messages: Dict[str, Any]) -> Any:
        """Process messages and return relevant data."""
        pass


class SQLQuerySystemTools:
    """
    A class that encapsulates SQL querying functionality with LLM integration
    using LangGraph for workflow management.
    """
    
    def __init__(self, db_path: str = "./db.sqlite3", system_prompt: str = None):
        """
        Initialize the SQL Query System Tools.
        
        Args:
            db_path: Path to the SQLite database file
            system_prompt: System prompt for the LLM (defaults to config value)
        """
        self.db_path = db_path
        self.system_prompt = system_prompt or config.LLM_SYSTEM_PROMPT_WITH_TOOLS
        self.logger = logging.getLogger(__name__)
        
        # Initialize database and tools
        self._setup_database()
        self._setup_llm()
        self._setup_graph()

    def _setup_database(self):
        """Setup the database connection and SQL query tool."""
        self.db = SQLDatabase.from_uri(f"sqlite:///{self.db_path}")
        self.sql_query_tool = QuerySQLDatabaseTool(db=self.db)
        
        # Create tool description with database info
        self.tool_description = """
        Tool for querying a SQL database.
            Execute a SQL query against the database and get back the result..
            If the query is not correct, an error message will be returned.
            If an error is returned, rewrite the query, check the query, and try again.

            args: 
                query: str = A detailed and correct SQL query.

            SQL dialect: {dialect}
            Database tables description: {database_info}
        """.format(
            dialect=self.db.dialect,
            database_info=self.db.get_table_info()
        )
    
    def _setup_llm(self):
        """Setup the language model with tools."""
        self.llm = init_chat_model(
            model=config.LLM_MODEL,
            model_provider=config.LLM_PROVIDER,
            api_key=settings.ANTHROPIC_API_KEY
        )
        
        # Create the SQL query tool
        @tool(description=self.tool_description)
        def sql_db_query(query: str) -> str:
            """Execute a SQL query against the database."""
            query_tool = QuerySQLDatabaseTool(db=self.db)
            try:
                result = query_tool.invoke(query)
                self.logger.info(f"Query executed successfully, result length: {len(str(result))}")
                return result
            except Exception as e:
                self.logger.error(f"Error executing SQL query: {e}")
                return f"Error executing SQL query: {e}"
        
        self.sql_db_query = sql_db_query
        self.llm_with_tools = self.llm.bind_tools([sql_db_query])
    
    def _setup_graph(self):
        """Setup the LangGraph workflow."""
        def chatbot(state: State, runtime: Runtime[ContextSchema]):
            response = self.llm_with_tools.invoke([runtime.context["system_prompt"]] + state["messages"])
            return {'messages': [response]}
        
        self.graph_builder = StateGraph(State, context_schema=ContextSchema)
        self.graph_builder.add_node("chatbot", chatbot)
        
        tool_node = ToolNode([self.sql_db_query])
        self.graph_builder.add_node("tools", tool_node)
        
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("tools", "chatbot")
        
        self.graph = self.graph_builder.compile()
    
    def query(self, messages: list, custom_system_prompt: str = None) -> Dict[str, Any]:
        """
        Execute a query using the LLM with SQL tools.
        
        Args:
            message: The user's query/message
            custom_system_prompt: Optional custom system prompt for this query
            
        Returns:
            Dictionary containing the conversation state with messages
        """
        system_prompt = custom_system_prompt or self.system_prompt
        
        state = self.graph.invoke(
            {"messages": messages}, 
            context={"system_prompt": SystemMessage(content=system_prompt)}
        )
        return state

    def query_and_process(self, messages: list, processor: MessageProcessor, 
                         custom_system_prompt: str = None) -> Any:
        """
        Execute a query and process the results using the provided processor.
        
        Args:
            messages: The user's query/messages
            processor: MessageProcessor instance to process the results
            custom_system_prompt: Optional custom system prompt
            
        Returns:
            Processed results from the processor
        """
        result = self.query(messages, custom_system_prompt)
        return processor.process_messages(result)


class ProcessedMessages(MessageProcessor):
    """
    A class to process and extract information from conversation messages.
    """
    
    def __init__(self, messages: Optional[Dict[str, Any]] = None):
        """
        Initialize ProcessedMessages.
        
        Args:
            messages: Optional messages dictionary to process immediately
        """
        self.messages = messages
        self._sql_queries = None
        self._human_messages = None
        self._ai_messages = None
        self._system_messages = None
        
        if messages:
            self._process_all()

    def process_messages(self, messages: Dict[str, Any]) -> 'ProcessedMessages':
        """
        Process messages and return self for method chaining.
        
        Args:
            messages: Dictionary containing conversation messages
            
        Returns:
            Self for method chaining
        """
        self.messages = messages
        self._process_all()
        return self

    def _process_all(self):
        """Process all message types and cache results."""
        if not self.messages:
            return
            
        self._sql_queries = self._extract_sql_queries()
        self._human_messages = self._get_messages_by_type(HumanMessage)
        self._ai_messages = self._get_messages_by_type(AIMessage)
        self._system_messages = self._get_messages_by_type(SystemMessage)
        self._tool_messages = self._get_messages_by_type(ToolMessage)

    def _extract_sql_queries(self) -> List[str]:
        """Extract SQL queries from the messages with improved error handling."""
        if not self.messages or 'messages' not in self.messages:
            return []
            
        sql_queries = []
        
        try:
            for message in self.messages['messages']:
                if isinstance(message, AIMessage):
                    # Handle different content structures
                    if hasattr(message, 'content'):
                        content = message.content
                        
                        # If content is a list, iterate through it
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and 'input' in item:
                                    if isinstance(item['input'], dict) and 'query' in item['input']:
                                        sql_queries.append(item['input']['query'])
                        
                        # Handle tool calls in message
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            for tool_call in message.tool_calls:
                                if hasattr(tool_call, 'args') and isinstance(tool_call.args, dict):
                                    if 'query' in tool_call.args:
                                        sql_queries.append(tool_call.args['query'])
                                        
        except Exception as e:
            logger.error(f"Error extracting SQL queries: {e}")
            
        return sql_queries

    def _get_messages_by_type(self, message_type: Union[HumanMessage, SystemMessage, AIMessage]) -> List[str]:
        """Get messages of a specific type from the conversation with error handling."""
        if not self.messages or 'messages' not in self.messages:
            return []
            
        filtered_messages = []
        
        try:
            for message in self.messages['messages']:
                if isinstance(message, message_type):
                    filtered_messages.append(message.content)
        except Exception as e:
            logger.error(f"Error filtering messages by type {message_type.__name__}: {e}")
            
        return filtered_messages

    @property
    def sql_queries(self) -> List[str]:
        """Get extracted SQL queries (cached)."""
        if self._sql_queries is None:
            self._sql_queries = self._extract_sql_queries()
        return self._sql_queries

    @property
    def human_messages(self) -> List[str]:
        """Get human messages (cached)."""
        if self._human_messages is None:
            self._human_messages = self._get_messages_by_type(HumanMessage)
        return self._human_messages

    @property
    def ai_messages(self) -> List[str]:
        """Get AI messages (cached)."""
        if self._ai_messages is None:
            self._ai_messages = self._get_messages_by_type(AIMessage)
        return self._ai_messages

    @property
    def system_messages(self) -> List[str]:
        """Get system messages (cached)."""
        if self._system_messages is None:
            self._system_messages = self._get_messages_by_type(SystemMessage)
        return self._system_messages
    
    @property
    def tool_messages(self) -> List[str]:
        """Get tool messages (cached)."""
        if self._tool_messages is None:
            self._tool_messages = self._get_messages_by_type(ToolMessage)
        return self._tool_messages

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all processed message data."""
        return {
            'total_messages': len(self.messages.get('messages', [])) if self.messages else 0,
            'sql_queries_count': len(self.sql_queries),
            'human_messages_count': len(self.human_messages),
            'ai_messages_count': len(self.ai_messages),
            'system_messages_count': len(self.system_messages),
            'sql_queries': self.sql_queries,
        }


def convert_queryset_to_langchain(messages_queryset) -> List[Union[HumanMessage, AIMessage]]:
    """
    Convert Django QuerySet of ChatMessage objects to LangChain message objects.
    
    Args:
        messages_queryset: Django QuerySet of ChatMessage objects with 'message_type' and 'content' fields
        
    Returns:
        List of LangChain message objects (HumanMessage, AIMessage)
    """
    langchain_messages = []
    
    for message in messages_queryset:
        if message.message_type == 'user':
            langchain_messages.append(HumanMessage(content=message.content))
        else:  # assistant
            langchain_messages.append(AIMessage(content=message.content))
    
    return langchain_messages


def get_user_filters(messages_queryset) -> List[tuple]:
    """
    Get user filters from the conversation history.
    """
    filters = []
    for message in messages_queryset:
        if message.message_type == 'assistant' and message.generated_sql:
            filters.append((message.generated_sql, message.sql_result))
    return filters