"""
ATUM Copilot Safety Layer
Prompt injection defense, input sanitization, and citation gating.
"""
import re
import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass
class SafetyResult:
    blocked: bool
    reasons: List[str]
    sanitized_input: Optional[str] = None


@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[str] = None


@dataclass
class CopilotTrace:
    run_id: str
    organization_id: str
    ticket_id: Optional[str]
    input_text: str
    plan: List[str]
    tool_calls: List[Dict]
    model_id: str
    confidence: float
    citations: List[Dict]
    final_output: Dict
    blocked: bool
    block_reasons: List[str]
    created_at: datetime


class CopilotSafety:
    """
    Central safety layer for ATUM Copilot.
    Enforces instruction hierarchy, sanitizes inputs, validates tool calls,
    and gates output on citations.
    """
    
    # Known injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+(instructions?|commands?|rules?)",
        r"disregard\s+(your\s+)?(instructions?|rules?|guidelines?)",
        r"forget\s+(everything|all\s+instructions|the\s+above)",
        r"system\s*(prompt|override|instruction)",
        r"you\s+are\s+(now|no\s+longer)\s+(a|an)\s+.*assistant",
        r"override\s+(your\s+)?safety",
        r"reveal\s+(your|the)\s+(system\s+)?(prompt|instructions|guidelines)",
        r"new\s+system\s+instructions?",
        r"\\(system\\s+message\\)",
        r"<!system>",
        r"\\[/SYSTEM\\]",
        r"#system_prompt",
        r"prompt:\s*\"",
        r"instructions:\s*\"",
        r"ignore\s+directive",
        r"jailbreak",
        r"dan\s+mode",
        r"developer\s+mode",
        r"super\s+assistant",
    ]
    
    # Compiled patterns for performance
    _injection_regex = re.compile('|'.join(INJECTION_PATTERNS), re.IGNORECASE)
    
    # Max input length
    MAX_INPUT_LENGTH = 8000
    
    # Safe tool whitelist
    SAFE_TOOLS = {
        "rag.search_kb",
        "rag.similar_tickets", 
        "tickets.classify",
        "comments.draft_reply",
        "sla.predict",
        "workflow.simulate",
    }
    
    # Citation threshold
    MIN_CITATION_CONFIDENCE = 0.5
    
    def __init__(self):
        self._injection_regex = re.compile('|'.join(self.INJECTION_PATTERNS), re.IGNORECASE)
    
    def sanitize_input(self, user_input: str) -> SafetyResult:
        """
        Sanitize user input by removing/escaping injection patterns.
        """
        reasons = []
        
        # Check for injection attempts
        matches = self._injection_regex.findall(user_input)
        if matches:
            reasons.append(f"Potential injection pattern detected: {matches[0] if matches else 'unknown'}")
        
        # Truncate if too long
        sanitized = user_input
        if len(user_input) > self.MAX_INPUT_LENGTH:
            sanitized = user_input[:self.MAX_INPUT_LENGTH]
            reasons.append(f"Input truncated from {len(user_input)} to {self.MAX_INPUT_LENGTH} characters")
        
        # Remove/escape HTML/JS
        sanitized = self._strip_dangerous_html(sanitized)
        
        # Check for cross-tenant attempts
        if self._contains_cross_tenant_attempt(sanitized):
            reasons.append("Cross-tenant data access attempt detected")
        
        blocked = len(reasons) > 0
        
        return SafetyResult(
            blocked=blocked,
            reasons=reasons,
            sanitized_input=sanitized if not blocked else None
        )
    
    def _strip_dangerous_html(self, text: str) -> str:
        """Strip dangerous HTML/JS content"""
        # Remove script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        # Remove on* event handlers
        text = re.sub(r'\s*on\w+\s*=\s*["\'].*?["\']', '', text, flags=re.IGNORECASE)
        # Remove javascript: URLs
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        return text
    
    def _contains_cross_tenant_attempt(self, text: str) -> bool:
        """Check for cross-tenant data access attempts"""
        patterns = [
            r"(other|another|different)\s+(org|organization|tenant|company)",
            r"show\s+me\s+(all|every)\s+(tickets?|users?|data)",
            r"bypass\s+(rls|row\s+level\s+security)",
        ]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def validate_tools(self, requested_tools: List[str]) -> tuple[bool, List[str]]:
        """
        Validate that only whitelisted tools are requested.
        Returns (is_valid, rejected_tools)
        """
        rejected = []
        for tool in requested_tools:
            if tool not in self.SAFE_TOOLS:
                rejected.append(tool)
        
        return len(rejected) == 0, rejected
    
    def validate_citations(self, output: Dict) -> tuple[bool, List[str]]:
        """
        Validate that output has proper citations.
        Returns (has_citations, missing_reasons)
        """
        reasons = []
        
        # Check for evidence in output
        evidence = output.get("evidence", [])
        if not evidence:
            reasons.append("No evidence/citations provided")
            return False, reasons
        
        # Check confidence threshold
        confidence = output.get("confidence", 0.0)
        if confidence < self.MIN_CITATION_CONFIDENCE:
            reasons.append(f"Confidence {confidence} below threshold {self.MIN_CITATION_CONFIDENCE}")
        
        # Check that evidence has required fields
        for item in evidence:
            if not all(k in item for k in ["type", "id", "title", "snippet"]):
                reasons.append("Evidence missing required fields (type, id, title, snippet)")
        
        return len(reasons) == 0, reasons
    
    def build_safe_output(self, 
                         suggestions: List[Dict] = None,
                         evidence: List[Dict] = None,
                         actions: List[Dict] = None,
                         confidence: float = 0.0,
                         blocked: bool = False,
                         block_reasons: List[str] = None) -> Dict:
        """
        Build safe output schema - always valid JSON with required structure.
        """
        return {
            "suggested_replies": suggestions or [],
            "evidence": evidence or [],
            "recommended_actions": actions or [],
            "confidence": max(0.0, min(1.0, confidence)),
            "safety": {
                "blocked": blocked,
                "reasons": block_reasons or []
            }
        }
    
    def insufficient_evidence_response(self) -> Dict:
        """
        Return safe 'insufficient evidence' response when citations missing.
        """
        return self.build_safe_output(
            suggestions=[{
                "text": "I don't have enough information to make a confident suggestion. Please provide more context or details about the ticket.",
                "tone": "helpful",
                "citations": [],
                "confidence": 0.0
            }],
            evidence=[],
            actions=[],
            confidence=0.0,
            blocked=True,
            block_reasons=["Insufficient evidence - no citations from knowledge base"]
        )


# Global safety instance
_copilot_safety: Optional[CopilotSafety] = None


def get_copilot_safety() -> CopilotSafety:
    """Get or create the global CopilotSafety instance"""
    global _copilot_safety
    if _copilot_safety is None:
        _copilot_safety = CopilotSafety()
    return _copilot_safety
