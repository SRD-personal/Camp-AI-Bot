"""
AI Tools models for function calling and web scraping
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
import enum
from app.core.database import Base
from app.core.config import settings


class ToolType(str, enum.Enum):
    """AI Tool types"""
    KNOWLEDGE_BASE = "knowledge_base"
    WEB_SCRAPER = "web_scraper"
    DOCUMENT_SEARCH = "document_search"
    CALCULATOR = "calculator"
    CODE_EXECUTOR = "code_executor"


class ToolStatus(str, enum.Enum):
    """Tool status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class AITool(Base):
    """AI Tool definition for Gemini function calling"""
    
    __tablename__ = "ai_tools"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    
    tool_type = Column(SQLEnum(ToolType), nullable=False)
    status = Column(SQLEnum(ToolStatus), default=ToolStatus.ACTIVE, nullable=False)
    
    config = Column(JSON, nullable=True)  # tool-specific configuration
    source_urls = Column(JSON, nullable=True)  # for web scrapers
    function_definition = Column(JSON, nullable=False)  # Gemini function schema
    
    usage_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    tool_data = relationship("ToolData", back_populates="tool", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="tool")
    
    def __repr__(self):
        return f"<AITool {self.name} ({self.tool_type})>"


class ToolData(Base):
    """Data scraped/indexed by AI tools"""
    
    __tablename__ = "tool_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("ai_tools.id", ondelete="CASCADE"), nullable=False)
    
    source_url = Column(String(1000), nullable=True)
    source_type = Column(String(100), nullable=False)  # web_page, document, extracted_text
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.PGVECTOR_DIMENSION))

    tool_metadata = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    scraped_at = Column(DateTime, nullable=True)
    
    # Relationships
    tool = relationship("AITool", back_populates="tool_data")
    
    def __repr__(self):
        return f"<ToolData {self.title or self.source_url}>"


class CallStatus(str, enum.Enum):
    """Tool call status"""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"


class ToolCall(Base):
    """Record of AI tool invocations"""
    
    __tablename__ = "tool_calls"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    tool_id = Column(UUID(as_uuid=True), ForeignKey("ai_tools.id"), nullable=False)
    
    input_params = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    
    status = Column(SQLEnum(CallStatus), default=CallStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    tool = relationship("AITool", back_populates="tool_calls")
    
    def __repr__(self):
        return f"<ToolCall {self.tool_id} ({self.status})>"
