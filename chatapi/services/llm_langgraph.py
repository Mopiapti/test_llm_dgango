# llm_system.py
import logging
from typing import Dict, Any
from typing_extensions import TypedDict, Annotated

from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph import START, StateGraph
from django.conf import settings
from constance import config

# Configure logging
logger = logging.getLogger(__name__)


class State(TypedDict):
    """State object for the SQL query workflow."""
    question: str
    query: str
    sql_result: str
    answer: str


class QueryOutput(TypedDict):
    """Generated SQL query output."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]


class SQLQuerySystem:
    """Main class for handling LLM-powered SQL queries."""
    
    def __init__(self, db_uri: str = "sqlite:///./db.sqlite3"):
        """Initialize the SQL query system.
        
        Args:
            db_uri: Database connection URI
        """
        self.db = self._init_database(db_uri)
        self.llm = self._init_llm()
        self.query_tool = QuerySQLDatabaseTool(db=self.db)
        self.graph = self._build_graph()
    
    def _init_database(self, db_uri: str) -> SQLDatabase:
        """Initialize database connection."""
        try:
            return SQLDatabase.from_uri(db_uri)
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _init_llm(self):
        """Initialize the language model."""
        try:
            return init_chat_model(
                model=config.LLM_MODEL,
                model_provider=config.LLM_PROVIDER,
                api_key=settings.ANTHROPIC_API_KEY
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def _get_query_prompt_template(self) -> ChatPromptTemplate:
        """Get the prompt template for SQL query generation."""
        system_prompt = config.LLM_SYSTEM_PROMPT_FOR_SQL
        user_prompt = "Question: {input}"
        
        return ChatPromptTemplate([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
    
    def _get_answer_prompt_template(self) -> ChatPromptTemplate:
        """Get the prompt template for answer generation."""
        system_prompt = config.LLM_SYSTEM_PROMPT_FOR_REPLY
        user_prompt = "Question: {input}"
        
        return ChatPromptTemplate([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
    
    def write_query(self, state: State) -> Dict[str, str]:
        """Generate SQL query to fetch information.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dictionary with generated query
        """
        try:
            prompt_template = self._get_query_prompt_template()
            prompt = prompt_template.invoke({
                "dialect": self.db.dialect,
                "top_k": getattr(config, 'TOP_K', 10),
                "table_info": self.db.get_table_info(),
                "input": state["question"],
            })
            
            structured_llm = self.llm.with_structured_output(QueryOutput)
            result = structured_llm.invoke(prompt)
            
            logger.info(f"Generated SQL query: {result['query']}")
            return {"query": result["query"]}
            
        except Exception as e:
            logger.error(f"Error generating SQL query: {e}")
            return {"query": "SELECT 1;"}  # Fallback query
    
    def execute_query(self, state: State) -> Dict[str, str]:
        """Execute SQL query.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dictionary with query results
        """
        try:
            result = self.query_tool.invoke(state["query"])
            logger.info(f"Query executed successfully, result length: {len(str(result))}")
            return {"sql_result": result}
            
        except Exception as e:
            logger.error(f"Error executing SQL query: {e}")
            return {"sql_result": f"Error executing query: {str(e)}"}
    
    def generate_answer(self, state: State) -> Dict[str, str]:
        """Answer question using retrieved information as context.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dictionary with generated answer
        """
        try:
            prompt_template = self._get_answer_prompt_template()
            prompt = prompt_template.invoke({
                "input": state["question"],
                "query": state["query"],
                "sql_result": state["sql_result"],
            })
            
            response = self.llm.invoke(prompt, temperature=0.5)
            logger.info("Answer generated successfully")
            return {"answer": response.content}
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {"answer": "I apologize, but I encountered an error while generating the answer."}
    
    def _build_graph(self) -> Any:
        """Build the workflow graph."""
        graph_builder = StateGraph(State).add_sequence([
            self.write_query,
            self.execute_query,
            self.generate_answer
        ])
        
        graph_builder.add_edge(START, "write_query")
        return graph_builder.compile()
    
    def query(self, question: str, stream: bool = False) -> Dict[str, Any]:
        """Process a natural language question and return SQL results.
        
        Args:
            question: The natural language question
            stream: Whether to stream intermediate results
            
        Returns:
            Final state with question, query, sql_result, and answer
        """
        logger.info(f"Processing question: {question}")
        
        initial_state = {"question": question}
        
        if stream:
            final_state = None
            for step in self.graph.stream(initial_state, stream_mode="updates"):
                logger.debug(f"Workflow step: {step}")
                final_state = step
            return final_state
        else:
            return self.graph.invoke(initial_state)