"""
Admin API endpoints for KB management
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.violation import ViolationLog
from app.services.document_service import DocumentService
from app.api.chat import get_current_user


router = APIRouter()


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role"""
    if user.role not in [UserRole.ADMIN, UserRole.HOD]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


@router.post("/kb/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload document for knowledge base
    
    - Admin/HOD only
    - Processes document and creates embeddings
    - Returns document info
    """
    try:
        document_service = DocumentService(db)
        
        # Process document
        document = await document_service.process_document(
            file_content=file.file,
            filename=file.filename,
            title=title,
            user=user,
            description=description,
            department=department or user.department
        )
        
        return {
            "document_id": str(document.id),
            "title": document.title,
            "file_path": document.file_path,
            "chunks_count": document.chunks_count,
            "embeddings_created": document.embeddings_count,
            "status": document.status,
            "created_at": document.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {str(e)}"
        )


@router.get("/kb/documents")
async def list_documents(
    page: int = 1,
    limit: int = 20,
    department: Optional[str] = None,
    search: Optional[str] = None,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List all knowledge base documents
    
    - Admin/HOD only
    - Returns paginated list of documents
    """
    try:
        # Build query
        stmt = select(Document)
        
        if department:
            stmt = stmt.where(Document.department == department)
        
        if search:
            stmt = stmt.where(Document.title.ilike(f"%{search}%"))
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await db.execute(count_stmt)
        total = result.scalar()
        
        # Get paginated results
        offset = (page - 1) * limit
        stmt = stmt.order_by(Document.created_at.desc()).offset(offset).limit(limit)
        
        result = await db.execute(stmt)
        documents = result.scalars().all()
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "documents": [
                {
                    "id": str(doc.id),
                    "title": doc.title,
                    "department": doc.department,
                    "file_size": doc.file_size,
                    "chunks_count": doc.chunks_count,
                    "status": doc.status,
                    "created_at": doc.created_at.isoformat()
                }
                for doc in documents
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/kb/documents/{document_id}")
async def delete_document(
    document_id: str,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete document and associated chunks/embeddings
    
    - Admin/HOD only
    """
    try:
        stmt = select(Document).where(Document.id == document_id)
        result = await db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        await db.delete(document)
        await db.commit()
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/violations")
async def list_violations(
    page: int = 1,
    limit: int = 50,
    severity: Optional[str] = None,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    List violation logs (append-only)
    
    - Admin/HOD only
    - Returns paginated violation logs
    """
    try:
        stmt = select(ViolationLog)
        
        if severity:
            stmt = stmt.where(ViolationLog.severity == severity)
        
        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        result = await db.execute(count_stmt)
        total = result.scalar()
        
        # Get paginated results
        offset = (page - 1) * limit
        stmt = stmt.order_by(ViolationLog.timestamp.desc()).offset(offset).limit(limit)
        
        result = await db.execute(stmt)
        violations = result.scalars().all()
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "violations": [v.to_dict() for v in violations]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list violations: {str(e)}"
        )


@router.get("/stats")
async def get_stats(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system statistics
    
    - Admin/HOD only
    - Returns overview statistics
    """
    try:
        from app.models.chat import ChatSession, Message
        
        # User stats
        user_count_stmt = select(func.count(User.id))
        result = await db.execute(user_count_stmt)
        total_users = result.scalar()
        
        # Document stats
        doc_count_stmt = select(func.count(Document.id))
        result = await db.execute(doc_count_stmt)
        total_documents = result.scalar()
        
        # Chat stats
        session_count_stmt = select(func.count(ChatSession.id))
        result = await db.execute(session_count_stmt)
        total_sessions = result.scalar()
        
        message_count_stmt = select(func.count(Message.id))
        result = await db.execute(message_count_stmt)
        total_messages = result.scalar()
        
        # Violation stats
        violation_count_stmt = select(func.count(ViolationLog.id))
        result = await db.execute(violation_count_stmt)
        total_violations = result.scalar()
        
        return {
            "users": {
                "total": total_users
            },
            "knowledge_base": {
                "total_documents": total_documents
            },
            "chat": {
                "total_conversations": total_sessions,
                "total_messages": total_messages
            },
            "violations": {
                "total_violations": total_violations
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )
