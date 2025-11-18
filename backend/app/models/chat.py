"""
Chat and messaging models
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class ChatSession(Base):
    """Chat session for grouping conversations"""
    
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    title = Column(String(500), nullable=True)
    session_type = Column(String(50), default="knowledge_base", nullable=False)  # knowledge_base, teacher_student
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)
    
    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession {self.id}>"


class Message(Base):
    """Individual message in a chat session"""
    
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # For RAG responses
    sources = Column(Text, nullable=True)  # JSON string of source documents
    tool_calls = Column(Text, nullable=True)  # JSON string of tool calls made
    
    # Guardrails
    guardrail_passed = Column(Boolean, default=True)
    guardrail_violations = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    violations = relationship("ViolationLog", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Message {self.role}: {self.content[:50]}>"
