"""
Document and knowledge base models
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import uuid
from app.core.database import Base
from app.core.config import settings


class Document(Base):
    """Document model for uploaded files"""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(1000), nullable=False)
    file_name = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    file_type = Column(String(50), nullable=False)  # pdf, docx, txt
    
    department = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    status = Column(String(50), default="processing", nullable=False)  # processing, ready, failed
    chunks_count = Column(Integer, default=0)
    embeddings_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_embedded_at = Column(DateTime, nullable=True)
    
    # Relationships
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document {self.title}>"


class KnowledgeChunk(Base):
    """Knowledge chunks for RAG retrieval"""
    
    __tablename__ = "knowledge_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.PGVECTOR_DIMENSION))
    
    metadata = Column(JSON, nullable=True)  # page number, section, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    def __repr__(self):
        return f"<KnowledgeChunk {self.document_id}:{self.chunk_index}>"
