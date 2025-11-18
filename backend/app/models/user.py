"""
User model for authentication and authorization
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    TEACHER = "teacher"
    HOD = "hod"
    ADMIN = "admin"


class User(Base):
    """User model for storing user information"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    google_uid = Column(String(255), unique=True, nullable=False, index=True)
    picture = Column(String(500), nullable=True)
    
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    department = Column(String(100), nullable=True)
    year_of_study = Column(String(20), nullable=True)
    roll_number = Column(String(50), nullable=True, unique=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": str(self.id),
            "email": self.email,
            "name": self.name,
            "picture": self.picture,
            "role": self.role.value,
            "department": self.department,
            "year_of_study": self.year_of_study,
            "roll_number": self.roll_number,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }
