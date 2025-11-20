"""
RAG (Retrieval-Augmented Generation) service for knowledge base chatbot
"""
import re
import random
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.document import KnowledgeChunk
from app.models.ai_tools import ToolData
from app.core.config import settings


class RAGService:
    """Service for RAG-based question answering"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.embedding_model = 'models/embedding-001'

        self.similarity_threshold = settings.SIMILARITY_THRESHOLD

        # Greeting patterns
        self.greeting_patterns = [
            r'\b(hi|hello|hey|hiya|greetings|good\s+(morning|afternoon|evening|day))\b',
            r'\b(what\'s\s+up|whats\s+up|sup|howdy)\b',
            r'\b(how\s+are\s+you|how\s+do\s+you\s+do)\b',
            r'^(hi|hello|hey)[\s!?.]*$'
        ]

        # Greeting responses
        self.greeting_responses = [
            "Hello! I'm KIT CampusAI, your virtual assistant for Kalaimagal Institute of Technology. How can I help you today?",
            "Hi there! Welcome to KIT CampusAI. I'm here to answer your questions about Kalaimagal Institute of Technology. What would you like to know?",
            "Hey! I'm your KIT assistant. Feel free to ask me anything about courses, admissions, campus facilities, or anything related to KIT!",
            "Greetings! I'm here to help you with information about Kalaimagal Institute of Technology. What can I assist you with?",
            "Hello! Welcome to KIT CampusAI. Ask me anything about Kalaimagal Institute of Technology and I'll do my best to help!"
        ]

    def _is_greeting(self, text: str) -> bool:
        """
        Check if the text is a greeting

        Args:
            text: Input text to check

        Returns:
            True if text is a greeting
        """
        text_lower = text.lower().strip()

        # Check against greeting patterns
        for pattern in self.greeting_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Make sure it's not a complex question
                # Simple heuristic: greetings are usually short
                if len(text.split()) <= 5:
                    return True

        return False

    def _generate_greeting_response(self) -> str:
        """
        Generate a friendly greeting response

        Returns:
            Random greeting response
        """
        return random.choice(self.greeting_responses)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Gemini
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {str(e)}")
    
    async def search_knowledge_base(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base using vector similarity

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            department: Optional department filter

        Returns:
            List of relevant chunks with similarity scores
        """
        # Format embedding as PostgreSQL array string for pgvector
        # Using string formatting for embedding since it's safe (controlled float array)
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

        # Build query for pgvector similarity search
        # Embedding is formatted directly in SQL to avoid SQLAlchemy parameter binding issues
        if department:
            query = text(f"""
                SELECT
                    kc.id,
                    kc.content,
                    kc.chunk_index,
                    kc.chunk_metadata,
                    d.title as document_title,
                    d.department,
                    d.file_name,
                    1 - (kc.embedding <=> '{embedding_str}'::vector) as similarity
                FROM knowledge_chunks kc
                JOIN documents d ON kc.document_id = d.id
                WHERE d.status = 'ready'
                AND d.department = :department
                AND 1 - (kc.embedding <=> '{embedding_str}'::vector) > :threshold
                ORDER BY kc.embedding <=> '{embedding_str}'::vector
                LIMIT :top_k
            """)
            params = {
                'threshold': self.similarity_threshold,
                'top_k': top_k,
                'department': department
            }
        else:
            query = text(f"""
                SELECT
                    kc.id,
                    kc.content,
                    kc.chunk_index,
                    kc.chunk_metadata,
                    d.title as document_title,
                    d.department,
                    d.file_name,
                    1 - (kc.embedding <=> '{embedding_str}'::vector) as similarity
                FROM knowledge_chunks kc
                JOIN documents d ON kc.document_id = d.id
                WHERE d.status = 'ready'
                AND 1 - (kc.embedding <=> '{embedding_str}'::vector) > :threshold
                ORDER BY kc.embedding <=> '{embedding_str}'::vector
                LIMIT :top_k
            """)
            params = {
                'threshold': self.similarity_threshold,
                'top_k': top_k
            }

        result = await self.db.execute(query, params)
        rows = result.fetchall()
        
        return [
            {
                'id': str(row.id),
                'content': row.content,
                'chunk_index': row.chunk_index,
                'metadata': row.chunk_metadata,
                'document_title': row.document_title,
                'department': row.department,
                'file_name': row.file_name,
                'similarity_score': float(row.similarity)
            }
            for row in rows
        ]
    
    async def search_tool_data(
        self,
        query_embedding: List[float],
        tool_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search AI tool data using vector similarity

        Args:
            query_embedding: Query embedding vector
            tool_id: Optional tool ID filter
            top_k: Number of results to return

        Returns:
            List of relevant tool data with similarity scores
        """
        # Format embedding as PostgreSQL array string for pgvector
        # Using string formatting for embedding since it's safe (controlled float array)
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'

        if tool_id:
            query = text(f"""
                SELECT
                    td.id,
                    td.title,
                    td.content,
                    td.source_url,
                    td.source_type,
                    td.tool_metadata,
                    at.name as tool_name,
                    1 - (td.embedding <=> '{embedding_str}'::vector) as similarity
                FROM tool_data td
                JOIN ai_tools at ON td.tool_id = at.id
                WHERE at.status = 'active'
                AND td.tool_id = :tool_id
                AND 1 - (td.embedding <=> '{embedding_str}'::vector) > :threshold
                ORDER BY td.embedding <=> '{embedding_str}'::vector
                LIMIT :top_k
            """)
            params = {
                'threshold': self.similarity_threshold,
                'top_k': top_k,
                'tool_id': tool_id
            }
        else:
            query = text(f"""
                SELECT
                    td.id,
                    td.title,
                    td.content,
                    td.source_url,
                    td.source_type,
                    td.tool_metadata,
                    at.name as tool_name,
                    1 - (td.embedding <=> '{embedding_str}'::vector) as similarity
                FROM tool_data td
                JOIN ai_tools at ON td.tool_id = at.id
                WHERE at.status = 'active'
                AND 1 - (td.embedding <=> '{embedding_str}'::vector) > :threshold
                ORDER BY td.embedding <=> '{embedding_str}'::vector
                LIMIT :top_k
            """)
            params = {
                'threshold': self.similarity_threshold,
                'top_k': top_k
            }

        result = await self.db.execute(query, params)
        rows = result.fetchall()
        
        return [
            {
                'id': str(row.id),
                'title': row.title,
                'content': row.content,
                'source_url': row.source_url,
                'source_type': row.source_type,
                'metadata': row.tool_metadata,
                'tool_name': row.tool_name,
                'similarity_score': float(row.similarity)
            }
            for row in rows
        ]
    
    async def generate_response(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate response using Gemini LLM with retrieved context
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            chat_history: Optional chat history for context
            
        Returns:
            Generated response
        """
        # Build context from chunks
        context = "\n\n".join([
            f"[Source: {chunk['document_title'] if 'document_title' in chunk else chunk.get('tool_name', 'Unknown')}]\n{chunk['content']}"
            for chunk in context_chunks
        ])
        
        # Build prompt
        system_prompt = """You are a helpful AI assistant for Kalaimagal Institute of Technology (KIT).
Your role is to answer questions based ONLY on the provided context from the knowledge base.

IMPORTANT RULES:
1. Only use information from the provided context
2. If the answer is not in the context, say "I don't have this information in my knowledge base."
3. Never share personal information, financial data, or confidential details
4. Be concise and accurate
5. Cite sources when possible
6. If asked about current events or information not in the knowledge base, politely decline

Context:
{context}
"""
        
        prompt = system_prompt.format(context=context)
        
        # Add chat history if provided
        if chat_history:
            conversation_context = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in chat_history[-5:]  # Last 5 messages
            ])
            prompt += f"\n\nRecent conversation:\n{conversation_context}"
        
        prompt += f"\n\nUser question: {query}\n\nAssistant:"
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise ValueError(f"Failed to generate response: {str(e)}")
    
    async def query(
        self,
        query: str,
        user_id: str,
        department: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
        use_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Process a query through the RAG pipeline

        Args:
            query: User query
            user_id: User ID
            department: Optional department filter
            chat_history: Optional chat history
            use_tools: Whether to search tool data

        Returns:
            Response with generated answer and sources
        """
        # Check if query is a greeting
        if self._is_greeting(query):
            return {
                'response': self._generate_greeting_response(),
                'sources': [],
                'confidence': 1.0
            }

        # Generate query embedding
        query_embedding = await self.generate_embedding(query)
        
        # Search knowledge base
        kb_chunks = await self.search_knowledge_base(
            query_embedding=query_embedding,
            top_k=5,
            department=department
        )
        
        # Search tool data if enabled
        tool_chunks = []
        if use_tools:
            tool_chunks = await self.search_tool_data(
                query_embedding=query_embedding,
                top_k=3
            )
        
        # Combine all chunks
        all_chunks = kb_chunks + tool_chunks
        
        # Sort by similarity
        all_chunks.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Take top results
        context_chunks = all_chunks[:8]
        
        if not context_chunks:
            return {
                'response': "I don't have enough information to answer this question. Please try rephrasing or ask about something else.",
                'sources': [],
                'confidence': 0.0
            }
        
        # Generate response
        response = await self.generate_response(
            query=query,
            context_chunks=context_chunks,
            chat_history=chat_history
        )
        
        # Calculate average confidence
        avg_confidence = sum(c['similarity_score'] for c in context_chunks) / len(context_chunks)
        
        return {
            'response': response,
            'sources': context_chunks,
            'confidence': avg_confidence
        }
