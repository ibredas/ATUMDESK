"""
Workflow Automation Engine - Domain Layer
Visual workflow builder with triggers, conditions, and actions
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from src.domain.entities import OrganizationId, TicketId, UserId


class TriggerType(Enum):
    """Types of workflow triggers"""
    TICKET_CREATED = "ticket_created"
    TICKET_UPDATED = "ticket_updated"
    TICKET_STATUS_CHANGED = "ticket_status_changed"
    TICKET_ASSIGNED = "ticket_assigned"
    SLA_BREACH_WARNING = "sla_breach_warning"
    SLA_BREACHED = "sla_breached"
    COMMENT_ADDED = "comment_added"
    TIME_BASED = "time_based"
    SCHEDULED = "scheduled"
    WEBHOOK_RECEIVED = "webhook_received"


class ActionType(Enum):
    """Types of workflow actions"""
    UPDATE_TICKET = "update_ticket"
    ASSIGN_TICKET = "assign_ticket"
    SEND_EMAIL = "send_email"
    SEND_NOTIFICATION = "send_notification"
    CREATE_TICKET = "create_ticket"
    ADD_COMMENT = "add_comment"
    ADD_TAG = "add_tag"
    SET_PRIORITY = "set_priority"
    SET_STATUS = "set_status"
    WEBHOOK_CALL = "webhook_call"
    AI_TRIAGE = "ai_triage"
    WAIT = "wait"
    CONDITIONAL_BRANCH = "conditional_branch"


class Operator(Enum):
    """Comparison operators for conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    IN = "in"
    NOT_IN = "not_in"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


@dataclass
class WorkflowCondition:
    """Condition for workflow branching"""
    id: UUID = field(default_factory=uuid4)
    field: str = ""  # e.g., "ticket.priority", "ticket.status"
    operator: Operator = Operator.EQUALS
    value: Any = None
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context"""
        field_value = self._get_field_value(context, self.field)
        
        if self.operator == Operator.EQUALS:
            return field_value == self.value
        elif self.operator == Operator.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == Operator.CONTAINS:
            return self.value in str(field_value)
        elif self.operator == Operator.GREATER_THAN:
            return field_value > self.value
        elif self.operator == Operator.LESS_THAN:
            return field_value < self.value
        elif self.operator == Operator.IN:
            return field_value in self.value
        elif self.operator == Operator.IS_EMPTY:
            return not field_value
        elif self.operator == Operator.IS_NOT_EMPTY:
            return bool(field_value)
        
        return False
    
    def _get_field_value(self, context: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested field path (e.g., 'ticket.priority')"""
        parts = field_path.split('.')
        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value


@dataclass
class WorkflowAction:
    """Action to execute in workflow"""
    id: UUID = field(default_factory=uuid4)
    action_type: ActionType = ActionType.UPDATE_TICKET
    config: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action with given context"""
        result = {"success": True, "action": self.action_type.value}
        
        if self.action_type == ActionType.UPDATE_TICKET:
            result["updates"] = self.config.get("fields", {})
        elif self.action_type == ActionType.ASSIGN_TICKET:
            result["assignee_id"] = self.config.get("assignee_id")
        elif self.action_type == ActionType.SEND_EMAIL:
            result["email"] = {
                "to": self.config.get("to"),
                "subject": self.config.get("subject"),
                "body": self.config.get("body"),
            }
        elif self.action_type == ActionType.ADD_COMMENT:
            result["comment"] = self.config.get("content")
        elif self.action_type == ActionType.SET_PRIORITY:
            result["priority"] = self.config.get("priority")
        elif self.action_type == ActionType.SET_STATUS:
            result["status"] = self.config.get("status")
        elif self.action_type == ActionType.WAIT:
            result["delay_seconds"] = self.config.get("delay", 0)
        elif self.action_type == ActionType.WEBHOOK_CALL:
            result["webhook"] = {
                "url": self.config.get("url"),
                "method": self.config.get("method", "POST"),
                "payload": self.config.get("payload"),
            }
        
        return result


@dataclass
class WorkflowStep:
    """Single step in workflow"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    action: WorkflowAction = field(default_factory=lambda: WorkflowAction())
    conditions: List[WorkflowCondition] = field(default_factory=list)
    next_step_id: Optional[UUID] = None
    on_failure_step_id: Optional[UUID] = None
    is_enabled: bool = True
    order: int = 0


@dataclass
class Workflow:
    """Workflow definition - Aggregate Root"""
    id: UUID = field(default_factory=uuid4)
    organization_id: OrganizationId = field(default=None)
    name: str = ""
    description: str = ""
    trigger_type: TriggerType = TriggerType.TICKET_CREATED
    trigger_config: Dict[str, Any] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)
    is_active: bool = True
    is_system: bool = False  # System workflows can't be deleted
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    created_by: UserId = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_step(self, step: WorkflowStep) -> None:
        """Add step to workflow"""
        step.order = len(self.steps)
        self.steps.append(step)
        self.updated_at = datetime.utcnow()
    
    def remove_step(self, step_id: UUID) -> bool:
        """Remove step from workflow"""
        self.steps = [s for s in self.steps if s.id != step_id]
        # Reorder remaining steps
        for i, step in enumerate(self.steps):
            step.order = i
        self.updated_at = datetime.utcnow()
        return True
    
    def reorder_steps(self, step_ids: List[UUID]) -> None:
        """Reorder workflow steps"""
        step_map = {s.id: s for s in self.steps}
        self.steps = [step_map[sid] for sid in step_ids if sid in step_map]
        for i, step in enumerate(self.steps):
            step.order = i
        self.updated_at = datetime.utcnow()
    
    def should_trigger(self, event_type: TriggerType, context: Dict[str, Any]) -> bool:
        """Check if workflow should trigger for event"""
        if not self.is_active:
            return False
        
        if self.trigger_type != event_type:
            return False
        
        # Check trigger-specific conditions
        if self.trigger_type == TriggerType.TICKET_STATUS_CHANGED:
            from_status = self.trigger_config.get("from_status")
            to_status = self.trigger_config.get("to_status")
            
            if from_status and context.get("old_status") != from_status:
                return False
            if to_status and context.get("new_status") != to_status:
                return False
        
        elif self.trigger_type == TriggerType.TIME_BASED:
            # Time-based triggers checked by scheduler
            pass
        
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with given context"""
        self.execution_count += 1
        results = []
        
        try:
            # Sort steps by order
            sorted_steps = sorted(self.steps, key=lambda s: s.order)
            
            current_step_idx = 0
            while current_step_idx < len(sorted_steps):
                step = sorted_steps[current_step_idx]
                
                if not step.is_enabled:
                    current_step_idx += 1
                    continue
                
                # Check conditions
                conditions_met = all(
                    cond.evaluate(context) for cond in step.conditions
                )
                
                if not conditions_met:
                    # Skip to next step
                    current_step_idx += 1
                    continue
                
                # Execute action
                try:
                    result = step.action.execute(context)
                    results.append({
                        "step_id": step.id,
                        "step_name": step.name,
                        "success": True,
                        "result": result,
                    })
                    
                    # Update context with result
                    context["last_action_result"] = result
                    
                    # Determine next step
                    if step.next_step_id:
                        # Find next step by ID
                        for i, s in enumerate(sorted_steps):
                            if s.id == step.next_step_id:
                                current_step_idx = i
                                break
                        else:
                            current_step_idx += 1
                    else:
                        current_step_idx += 1
                    
                except Exception as e:
                    results.append({
                        "step_id": step.id,
                        "step_name": step.name,
                        "success": False,
                        "error": str(e),
                    })
                    
                    # Handle failure
                    if step.on_failure_step_id:
                        for i, s in enumerate(sorted_steps):
                            if s.id == step.on_failure_step_id:
                                current_step_idx = i
                                break
                        else:
                            break
                    else:
                        break
            
            self.success_count += 1
            return {
                "workflow_id": self.id,
                "success": True,
                "results": results,
            }
            
        except Exception as e:
            self.failure_count += 1
            return {
                "workflow_id": self.id,
                "success": False,
                "error": str(e),
                "results": results,
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        success_rate = 0
        if self.execution_count > 0:
            success_rate = (self.success_count / self.execution_count) * 100
        
        return {
            "workflow_id": str(self.id),
            "name": self.name,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": round(success_rate, 2),
            "is_active": self.is_active,
            "steps_count": len(self.steps),
        }


@dataclass
class WorkflowExecution:
    """Record of workflow execution"""
    id: UUID = field(default_factory=uuid4)
    workflow_id: UUID = field(default=None)
    ticket_id: TicketId = field(default=None)
    organization_id: OrganizationId = field(default=None)
    trigger_event: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    results: List[Dict[str, Any]] = field(default_factory=list)
    success: bool = False
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    duration_ms: int = 0
    error_message: str = ""
    
    def complete(self, success: bool, results: List[Dict[str, Any]], error: str = ""):
        """Mark execution as complete"""
        self.completed_at = datetime.utcnow()
        self.success = success
        self.results = results
        self.error_message = error
        
        if self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds()
            self.duration_ms = int(duration * 1000)
