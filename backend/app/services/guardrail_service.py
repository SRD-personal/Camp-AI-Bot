"""
Guardrail service for input/output safety checks
"""
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.models.violation import ViolationSeverity
from app.core.config import settings


@dataclass
class GuardrailViolation:
    """Guardrail violation details"""
    rule: str
    severity: ViolationSeverity
    description: str
    matched_content: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class GuardrailResult:
    """Guardrail check result"""
    is_safe: bool
    violations: List[GuardrailViolation]
    original_text: str
    sanitized_text: str
    severity: ViolationSeverity


class GuardrailService:
    """Service for checking input/output safety"""
    
    # PII patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    SSN_PATTERN = r'\b\d{3}-\d{2}-\d{4}\b'
    CREDIT_CARD_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    AADHAR_PATTERN = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(;.*--)",
        r"('.*OR.*'=')",
    ]
    
    # Prompt injection patterns
    PROMPT_INJECTION_PATTERNS = [
        r"(ignore previous instructions)",
        r"(disregard.*rules)",
        r"(you are now)",
        r"(forget.*instructions)",
        r"(new instructions)",
        r"(system prompt)",
        r"(override.*settings)",
    ]
    
    # Financial data keywords
    FINANCIAL_KEYWORDS = [
        'salary', 'budget', 'cost', 'payment', 'invoice', 'account number',
        'bank account', 'credit card', 'debit card', 'transaction'
    ]
    
    def __init__(self):
        self.max_query_length = settings.MAX_QUERY_LENGTH
    
    async def check_input(self, query: str, user_id: str) -> GuardrailResult:
        """
        Check input query for safety violations
        
        Args:
            query: Input query to check
            user_id: User ID for logging
            
        Returns:
            GuardrailResult with violations if any
        """
        violations = []
        sanitized = query
        
        # Check query length
        if len(query) > self.max_query_length:
            violations.append(GuardrailViolation(
                rule="QUERY_LENGTH",
                severity=ViolationSeverity.LOW,
                description=f"Query exceeds max length of {self.max_query_length}",
                matched_content=f"{len(query)} characters"
            ))
            sanitized = query[:self.max_query_length]
        
        # Check for SQL injection
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                violations.append(GuardrailViolation(
                    rule="SQL_INJECTION",
                    severity=ViolationSeverity.HIGH,
                    description="Potential SQL injection detected",
                    matched_content=pattern
                ))
        
        # Check for prompt injection
        for pattern in self.PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                violations.append(GuardrailViolation(
                    rule="PROMPT_INJECTION",
                    severity=ViolationSeverity.HIGH,
                    description="Potential prompt injection detected",
                    matched_content=pattern
                ))
        
        # Determine overall severity
        max_severity = ViolationSeverity.LOW
        if violations:
            severity_order = {
                ViolationSeverity.LOW: 1,
                ViolationSeverity.MEDIUM: 2,
                ViolationSeverity.HIGH: 3
            }
            max_severity = max(violations, key=lambda v: severity_order[v.severity]).severity
        
        return GuardrailResult(
            is_safe=len([v for v in violations if v.severity == ViolationSeverity.HIGH]) == 0,
            violations=violations,
            original_text=query,
            sanitized_text=sanitized,
            severity=max_severity
        )
    
    async def check_output(self, response: str, sources: List[Dict[str, Any]]) -> GuardrailResult:
        """
        Check output response for safety violations
        
        Args:
            response: Generated response to check
            sources: Retrieved source documents
            
        Returns:
            GuardrailResult with violations if any
        """
        violations = []
        sanitized = response
        
        # Check for PII in response
        pii_found = []
        
        # Email
        emails = re.findall(self.EMAIL_PATTERN, response)
        if emails:
            pii_found.extend(emails)
            for email in emails:
                sanitized = sanitized.replace(email, "[EMAIL REDACTED]")
            violations.append(GuardrailViolation(
                rule="PII_SHARING",
                severity=ViolationSeverity.HIGH,
                description="Email addresses detected in response",
                matched_content=", ".join(emails[:3]),
                details={"pii_type": "email", "count": len(emails)}
            ))
        
        # Phone numbers
        phones = re.findall(self.PHONE_PATTERN, response)
        if phones:
            pii_found.extend(phones)
            for phone in phones:
                sanitized = sanitized.replace(phone, "[PHONE REDACTED]")
            violations.append(GuardrailViolation(
                rule="PII_SHARING",
                severity=ViolationSeverity.HIGH,
                description="Phone numbers detected in response",
                matched_content=", ".join(phones[:3]),
                details={"pii_type": "phone", "count": len(phones)}
            ))
        
        # SSN/Aadhar
        ssns = re.findall(self.SSN_PATTERN, response)
        aadhars = re.findall(self.AADHAR_PATTERN, response)
        if ssns or aadhars:
            for ssn in ssns:
                sanitized = sanitized.replace(ssn, "[ID REDACTED]")
            for aadhar in aadhars:
                sanitized = sanitized.replace(aadhar, "[ID REDACTED]")
            violations.append(GuardrailViolation(
                rule="PII_SHARING",
                severity=ViolationSeverity.HIGH,
                description="ID numbers detected in response",
                details={"pii_type": "id_number", "count": len(ssns) + len(aadhars)}
            ))
        
        # Check for financial data
        financial_found = []
        for keyword in self.FINANCIAL_KEYWORDS:
            if keyword.lower() in response.lower():
                financial_found.append(keyword)
        
        if financial_found:
            violations.append(GuardrailViolation(
                rule="FINANCIAL_DATA",
                severity=ViolationSeverity.MEDIUM,
                description="Financial information detected in response",
                matched_content=", ".join(financial_found[:5]),
                details={"keywords": financial_found}
            ))
        
        # Check if response is grounded in sources
        if not sources or len(sources) == 0:
            violations.append(GuardrailViolation(
                rule="KNOWLEDGE_BASE",
                severity=ViolationSeverity.LOW,
                description="Response may not be grounded in knowledge base",
                details={"source_count": 0}
            ))
        
        # Determine overall severity
        max_severity = ViolationSeverity.LOW
        if violations:
            severity_order = {
                ViolationSeverity.LOW: 1,
                ViolationSeverity.MEDIUM: 2,
                ViolationSeverity.HIGH: 3
            }
            max_severity = max(violations, key=lambda v: severity_order[v.severity]).severity
        
        return GuardrailResult(
            is_safe=len([v for v in violations if v.severity == ViolationSeverity.HIGH]) == 0,
            violations=violations,
            original_text=response,
            sanitized_text=sanitized,
            severity=max_severity
        )
    
    def is_safe_for_delivery(self, result: GuardrailResult) -> bool:
        """
        Check if result is safe to deliver to user
        
        Args:
            result: Guardrail check result
            
        Returns:
            True if safe, False otherwise
        """
        # Block if any HIGH severity violations
        high_violations = [v for v in result.violations if v.severity == ViolationSeverity.HIGH]
        return len(high_violations) == 0
