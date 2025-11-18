"""
Chat API endpoints for RAG chatbot
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.rag_service import RAGService
from app.services.guardrail_service import GuardrailService
from app.models.user import User
from app.models.chat import ChatSession, Message
from app.models.violation import ViolationLog


router = APIRouter()


class ChatQueryRequest(BaseModel):
    """Chat query request"""
    query: str
    conversation_id: Optional[str] = None


class ChatQueryResponse(BaseModel):
    """Chat query response"""
    message_id: str
    response: str
    sources: List[dict]
    timestamp: str
    guardrail_checks: dict
    confidence: float = 0.0


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    if not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = authorization.split('Bearer ')[1]
    auth_service = AuthService(db)
    
    try:
        user = await auth_service.get_current_user(token)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(
    request: ChatQueryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit a query to the RAG chatbot
    
    - Checks input guardrails
    - Retrieves relevant knowledge
    - Generates response with Gemini
    - Checks output guardrails
    - Logs conversation
    """
    try:
        # Initialize services
        guardrail_service = GuardrailService()
        rag_service = RAGService(db)
        
        # Check input guardrails
        input_check = await guardrail_service.check_input(request.query, str(user.id))
        
        if not input_check.is_safe:
            # Log high severity violations
            for violation in input_check.violations:
                if violation.severity.value == "HIGH":
                    violation_log = ViolationLog(
                        sender_id=user.id,
                        violation_rule=violation.rule,
                        severity=violation.severity,
                        original_message=request.query,
                        violation_details={"description": violation.description}
                    )
                    db.add(violation_log)
            
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Query violated guardrails: {', '.join([v.rule for v in input_check.violations])}"
            )
        
        # Get or create chat session
        if request.conversation_id:
            stmt = select(ChatSession).where(
                ChatSession.id == request.conversation_id,
                ChatSession.user_id == user.id
            )
            result = await db.execute(stmt)
            session = result.scalar_one_or_none()
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new session
            session = ChatSession(
                user_id=user.id,
                title=request.query[:100],
                session_type="knowledge_base"
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
        
        # Get chat history
        stmt = select(Message).where(Message.session_id == session.id).order_by(Message.created_at.desc()).limit(10)
        result = await db.execute(stmt)
        history_messages = result.scalars().all()
        
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(history_messages)
        ]
        
        # Query RAG service
        rag_result = await rag_service.query(
            query=input_check.sanitized_text,
            user_id=str(user.id),
            department=user.department,
            chat_history=chat_history,
            use_tools=True
        )
        
        # Check output guardrails
        output_check = await guardrail_service.check_output(
            rag_result['response'],
            rag_result['sources']
        )
        
        # Use sanitized response if needed
        final_response = output_check.sanitized_text if not output_check.is_safe else rag_result['response']
        
        # Log user message
        user_message = Message(
            session_id=session.id,
            role="user",
            content=request.query,
            guardrail_passed=input_check.is_safe
        )
        db.add(user_message)
        
        # Log assistant message
        assistant_message = Message(
            session_id=session.id,
            role="assistant",
            content=final_response,
            sources=str(rag_result['sources']),
            guardrail_passed=output_check.is_safe,
            guardrail_violations=str([v.__dict__ for v in output_check.violations]) if output_check.violations else None
        )
        db.add(assistant_message)
        
        # Update session
        session.last_message_at = datetime.utcnow()
        
        # Log violations
        for violation in output_check.violations:
            if violation.severity.value in ["MEDIUM", "HIGH"]:
                violation_log = ViolationLog(
                    message_id=assistant_message.id,
                    sender_id=user.id,
                    violation_rule=violation.rule,
                    severity=violation.severity,
                    original_message=rag_result['response'],
                    violation_details={"description": violation.description}
                )
                db.add(violation_log)
        
        await db.commit()
        await db.refresh(assistant_message)
        
        return ChatQueryResponse(
            message_id=str(assistant_message.id),
            response=final_response,
            sources=rag_result['sources'],
            timestamp=assistant_message.created_at.isoformat(),
            guardrail_checks={
                "input_safe": input_check.is_safe,
                "output_safe": output_check.is_safe,
                "violations": [
                    {
                        "rule": v.rule,
                        "severity": v.severity.value,
                        "description": v.description
                    }
                    for v in input_check.violations + output_check.violations
                ]
            },
            confidence=rag_result.get('confidence', 0.0)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


@router.get("/history/{conversation_id}")
async def get_chat_history(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get chat history for a conversation
    
    - Returns all messages in the conversation
    """
    try:
        # Get session
        stmt = select(ChatSession).where(
            ChatSession.id == conversation_id,
            ChatSession.user_id == user.id
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        stmt = select(Message).where(Message.session_id == session.id).order_by(Message.created_at)
        result = await db.execute(stmt)
        messages = result.scalars().all()
        
        return {
            "conversation_id": str(session.id),
            "title": session.title,
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get chat history: {str(e)}"
        )


@router.get("/sessions")
async def get_chat_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all chat sessions for current user
    
    - Returns list of all conversations
    """
    try:
        stmt = select(ChatSession).where(
            ChatSession.user_id == user.id,
            ChatSession.is_active == True
        ).order_by(ChatSession.updated_at.desc())
        
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        
        return {
            "sessions": [
                {
                    "id": str(session.id),
                    "title": session.title,
                    "last_message_at": session.last_message_at.isoformat() if session.last_message_at else None,
                    "created_at": session.created_at.isoformat()
                }
                for session in sessions
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sessions: {str(e)}"
        )
