"""
Marketing Automation Workflow Engine
"""
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import uuid
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base
import asyncio
from dataclasses import dataclass
import traceback

from core.database import Base, get_db
from journey.lifecycle_manager import TouchpointType, LifecycleStage

logger = logging.getLogger(__name__)

class TriggerType(str, Enum):
    """Types of workflow triggers"""
    TIME_BASED = "time_based"
    BEHAVIOR_BASED = "behavior_based"
    LIFECYCLE_STAGE = "lifecycle_stage"
    CUSTOM_EVENT = "custom_event"
    API_TRIGGER = "api_trigger"
    EMAIL_ENGAGEMENT = "email_engagement"
    PURCHASE_EVENT = "purchase_event"
    SCORE_THRESHOLD = "score_threshold"

class ActionType(str, Enum):
    """Types of workflow actions"""
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    SEND_PUSH = "send_push"
    UPDATE_FIELD = "update_field"
    ADD_TO_SEGMENT = "add_to_segment"
    REMOVE_FROM_SEGMENT = "remove_from_segment"
    WAIT = "wait"
    WEBHOOK = "webhook"
    CREATE_TASK = "create_task"
    ADD_TAG = "add_tag"
    SCORE_UPDATE = "score_update"
    BRANCH = "branch"

class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    DRAFT = "draft"

# Database Models
class Workflow(Base):
    """Marketing automation workflow"""
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default=WorkflowStatus.DRAFT.value)
    trigger_config = Column(JSON, nullable=False)
    workflow_config = Column(JSON, nullable=False)  # Steps and actions
    target_audience = Column(JSON)  # Segmentation criteria
    performance_metrics = Column(JSON, default={})
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow")

class WorkflowExecution(Base):
    """Individual workflow execution instances"""
    __tablename__ = "workflow_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String, ForeignKey("workflows.id"), index=True)
    customer_id = Column(String, index=True)
    status = Column(String, default="started")
    current_step = Column(Integer, default=0)
    execution_data = Column(JSON, default={})  # Runtime variables
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    step_logs = relationship("WorkflowStepLog", back_populates="execution")

class WorkflowStepLog(Base):
    """Log of individual step executions"""
    __tablename__ = "workflow_step_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey("workflow_executions.id"), index=True)
    step_number = Column(Integer)
    step_type = Column(String)
    step_name = Column(String)
    status = Column(String)  # success, failed, skipped
    executed_at = Column(DateTime, default=datetime.now)
    execution_time_ms = Column(Integer)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    
    # Relationships
    execution = relationship("WorkflowExecution", back_populates="step_logs")

@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    name: str
    action_type: ActionType
    config: Dict[str, Any]
    conditions: List[Dict[str, Any]] = None
    delay_minutes: int = 0

@dataclass
class WorkflowTrigger:
    """Workflow trigger configuration"""
    trigger_type: TriggerType
    config: Dict[str, Any]
    conditions: List[Dict[str, Any]] = None

class WorkflowEngine:
    """Marketing automation workflow engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.action_handlers = {
            ActionType.SEND_EMAIL: self._handle_send_email,
            ActionType.SEND_SMS: self._handle_send_sms,
            ActionType.SEND_PUSH: self._handle_send_push,
            ActionType.UPDATE_FIELD: self._handle_update_field,
            ActionType.ADD_TO_SEGMENT: self._handle_add_to_segment,
            ActionType.REMOVE_FROM_SEGMENT: self._handle_remove_from_segment,
            ActionType.WAIT: self._handle_wait,
            ActionType.WEBHOOK: self._handle_webhook,
            ActionType.CREATE_TASK: self._handle_create_task,
            ActionType.ADD_TAG: self._handle_add_tag,
            ActionType.SCORE_UPDATE: self._handle_score_update,
            ActionType.BRANCH: self._handle_branch
        }
    
    def create_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """Create a new marketing workflow"""
        try:
            # Validate workflow configuration
            self._validate_workflow_config(workflow_config)
            
            workflow = Workflow(
                name=workflow_config["name"],
                description=workflow_config.get("description", ""),
                trigger_config=workflow_config["trigger"],
                workflow_config=workflow_config["steps"],
                target_audience=workflow_config.get("target_audience", {}),
                created_by=workflow_config.get("created_by", "system")
            )
            
            self.db.add(workflow)
            self.db.commit()
            
            logger.info(f"Created workflow: {workflow.name} ({workflow.id})")
            return workflow.id
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            self.db.rollback()
            raise
    
    def start_workflow(self, workflow_id: str) -> bool:
        """Start a workflow (activate triggers)"""
        try:
            workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow.status = WorkflowStatus.ACTIVE.value
            workflow.started_at = datetime.now()
            
            # Initialize trigger monitoring
            self._setup_workflow_triggers(workflow)
            
            self.db.commit()
            logger.info(f"Started workflow: {workflow.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            self.db.rollback()
            return False
    
    def trigger_workflow(self, workflow_id: str, customer_id: str, 
                        trigger_data: Dict[str, Any] = None) -> str:
        """Manually trigger a workflow for a specific customer"""
        try:
            workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            if workflow.status != WorkflowStatus.ACTIVE.value:
                raise ValueError(f"Workflow {workflow_id} is not active")
            
            # Check if customer meets target audience criteria
            if not self._customer_matches_criteria(customer_id, workflow.target_audience):
                logger.info(f"Customer {customer_id} doesn't match workflow criteria")
                return None
            
            # Create execution instance
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                customer_id=customer_id,
                execution_data=trigger_data or {}
            )
            
            self.db.add(execution)
            self.db.commit()
            
            # Start execution
            asyncio.create_task(self._execute_workflow(execution.id))
            
            logger.info(f"Triggered workflow {workflow_id} for customer {customer_id}")
            return execution.id
            
        except Exception as e:
            logger.error(f"Error triggering workflow: {e}")
            self.db.rollback()
            raise
    
    async def _execute_workflow(self, execution_id: str):
        """Execute workflow steps for a specific customer"""
        try:
            execution = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.id == execution_id
            ).first()
            
            if not execution:
                logger.error(f"Execution {execution_id} not found")
                return
            
            workflow = execution.workflow
            steps = workflow.workflow_config.get("steps", [])
            
            logger.info(f"Executing workflow {workflow.name} for customer {execution.customer_id}")
            
            for step_index, step_config in enumerate(steps):
                try:
                    # Check if execution should continue
                    if execution.status == "cancelled":
                        break
                    
                    step = WorkflowStep(
                        step_id=step_config.get("id", str(step_index)),
                        name=step_config.get("name", f"Step {step_index + 1}"),
                        action_type=ActionType(step_config["action_type"]),
                        config=step_config.get("config", {}),
                        conditions=step_config.get("conditions", []),
                        delay_minutes=step_config.get("delay_minutes", 0)
                    )
                    
                    # Update current step
                    execution.current_step = step_index
                    self.db.commit()
                    
                    # Check step conditions
                    if not self._evaluate_conditions(step.conditions, execution):
                        self._log_step_execution(execution.id, step_index, step.action_type.value, 
                                               step.name, "skipped", "Conditions not met")
                        continue
                    
                    # Apply delay if specified
                    if step.delay_minutes > 0:
                        await asyncio.sleep(step.delay_minutes * 60)
                    
                    # Execute step
                    start_time = datetime.now()
                    result = await self._execute_step(step, execution)
                    execution_time = (datetime.now() - start_time).total_seconds() * 1000
                    
                    # Log execution
                    self._log_step_execution(
                        execution.id, step_index, step.action_type.value, step.name,
                        "success" if result["success"] else "failed",
                        result.get("message", ""),
                        execution_time,
                        step.config,
                        result.get("output_data", {})
                    )
                    
                    # Handle branching
                    if step.action_type == ActionType.BRANCH and result["success"]:
                        branch_path = result.get("branch_path")
                        if branch_path:
                            # Jump to different step based on branch logic
                            continue
                    
                    # Stop if step failed and no error handling
                    if not result["success"] and not step.config.get("continue_on_error", False):
                        execution.status = "failed"
                        execution.error_message = result.get("message", "Step execution failed")
                        execution.completed_at = datetime.now()
                        self.db.commit()
                        break
                        
                except Exception as step_error:
                    logger.error(f"Step execution error: {step_error}")
                    self._log_step_execution(
                        execution.id, step_index, step_config.get("action_type", "unknown"),
                        step_config.get("name", f"Step {step_index + 1}"), "failed",
                        str(step_error)
                    )
                    
                    # Stop execution on step error
                    execution.status = "failed"
                    execution.error_message = str(step_error)
                    execution.completed_at = datetime.now()
                    self.db.commit()
                    break
            
            # Mark as completed if all steps successful
            if execution.status not in ["failed", "cancelled"]:
                execution.status = "completed"
                execution.completed_at = datetime.now()
                self.db.commit()
                
                logger.info(f"Workflow execution {execution_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            logger.error(traceback.format_exc())
            
            # Mark execution as failed
            execution = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.id == execution_id
            ).first()
            if execution:
                execution.status = "failed"
                execution.error_message = str(e)
                execution.completed_at = datetime.now()
                self.db.commit()
    
    async def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Execute a single workflow step"""
        try:
            handler = self.action_handlers.get(step.action_type)
            if not handler:
                return {"success": False, "message": f"No handler for action type: {step.action_type}"}
            
            result = await handler(step, execution)
            return result
            
        except Exception as e:
            logger.error(f"Step execution error: {e}")
            return {"success": False, "message": str(e)}
    
    # Action Handlers
    async def _handle_send_email(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle email sending action"""
        try:
            config = step.config
            template_id = config.get("template_id")
            subject = config.get("subject")
            personalization = config.get("personalization", {})
            
            # Get customer data for personalization
            customer_data = self._get_customer_data(execution.customer_id)
            
            # Simulate email sending (replace with actual email service)
            email_data = {
                "to": customer_data.get("email"),
                "subject": self._personalize_content(subject, customer_data, personalization),
                "template_id": template_id,
                "customer_id": execution.customer_id
            }
            
            # Log email sending
            logger.info(f"Sending email to {customer_data.get('email')} - Subject: {subject}")
            
            # Update execution data
            execution.execution_data.setdefault("emails_sent", []).append({
                "timestamp": datetime.now().isoformat(),
                "template_id": template_id,
                "subject": subject
            })
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "output_data": email_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"Email sending failed: {e}"}
    
    async def _handle_send_sms(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle SMS sending action"""
        try:
            config = step.config
            message = config.get("message")
            
            customer_data = self._get_customer_data(execution.customer_id)
            
            # Simulate SMS sending
            sms_data = {
                "to": customer_data.get("phone"),
                "message": self._personalize_content(message, customer_data),
                "customer_id": execution.customer_id
            }
            
            logger.info(f"Sending SMS to {customer_data.get('phone')}")
            
            return {
                "success": True,
                "message": "SMS sent successfully",
                "output_data": sms_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"SMS sending failed: {e}"}
    
    async def _handle_send_push(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle push notification action"""
        try:
            config = step.config
            title = config.get("title")
            message = config.get("message")
            
            customer_data = self._get_customer_data(execution.customer_id)
            
            # Simulate push notification
            push_data = {
                "customer_id": execution.customer_id,
                "title": self._personalize_content(title, customer_data),
                "message": self._personalize_content(message, customer_data)
            }
            
            logger.info(f"Sending push notification to {execution.customer_id}")
            
            return {
                "success": True,
                "message": "Push notification sent successfully",
                "output_data": push_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"Push notification failed: {e}"}
    
    async def _handle_update_field(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle customer field update action"""
        try:
            config = step.config
            field_name = config.get("field_name")
            field_value = config.get("field_value")
            
            # Update customer field in database
            from core.database import Customer
            customer = self.db.query(Customer).filter(
                Customer.customer_id == execution.customer_id
            ).first()
            
            if customer:
                # Update field if it exists
                if hasattr(customer, field_name):
                    setattr(customer, field_name, field_value)
                    self.db.commit()
                    
                    return {
                        "success": True,
                        "message": f"Updated {field_name} to {field_value}",
                        "output_data": {"field_name": field_name, "field_value": field_value}
                    }
                else:
                    return {"success": False, "message": f"Field {field_name} not found"}
            else:
                return {"success": False, "message": "Customer not found"}
                
        except Exception as e:
            return {"success": False, "message": f"Field update failed: {e}"}
    
    async def _handle_add_to_segment(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle add to segment action"""
        try:
            config = step.config
            segment_id = config.get("segment_id")
            
            # Add customer to segment
            from core.database import Customer
            customer = self.db.query(Customer).filter(
                Customer.customer_id == execution.customer_id
            ).first()
            
            if customer:
                customer.segment_id = segment_id
                self.db.commit()
                
                return {
                    "success": True,
                    "message": f"Added customer to segment {segment_id}",
                    "output_data": {"segment_id": segment_id}
                }
            else:
                return {"success": False, "message": "Customer not found"}
                
        except Exception as e:
            return {"success": False, "message": f"Segment addition failed: {e}"}
    
    async def _handle_remove_from_segment(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle remove from segment action"""
        try:
            # Implementation for removing from segment
            return {"success": True, "message": "Removed from segment"}
        except Exception as e:
            return {"success": False, "message": f"Segment removal failed: {e}"}
    
    async def _handle_wait(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle wait/delay action"""
        try:
            config = step.config
            wait_minutes = config.get("wait_minutes", 0)
            wait_hours = config.get("wait_hours", 0)
            wait_days = config.get("wait_days", 0)
            
            total_seconds = (wait_days * 24 * 3600) + (wait_hours * 3600) + (wait_minutes * 60)
            
            if total_seconds > 0:
                await asyncio.sleep(total_seconds)
            
            return {
                "success": True,
                "message": f"Waited {total_seconds} seconds",
                "output_data": {"wait_seconds": total_seconds}
            }
            
        except Exception as e:
            return {"success": False, "message": f"Wait action failed: {e}"}
    
    async def _handle_webhook(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle webhook action"""
        try:
            config = step.config
            url = config.get("url")
            method = config.get("method", "POST")
            headers = config.get("headers", {})
            
            # Simulate webhook call
            webhook_data = {
                "url": url,
                "method": method,
                "customer_id": execution.customer_id,
                "execution_id": execution.id
            }
            
            logger.info(f"Calling webhook: {url}")
            
            return {
                "success": True,
                "message": "Webhook called successfully",
                "output_data": webhook_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"Webhook call failed: {e}"}
    
    async def _handle_create_task(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle task creation action"""
        try:
            config = step.config
            task_type = config.get("task_type")
            assignee = config.get("assignee")
            description = config.get("description")
            
            # Create task (simulate)
            task_data = {
                "type": task_type,
                "assignee": assignee,
                "description": description,
                "customer_id": execution.customer_id,
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Created task: {task_type} for {assignee}")
            
            return {
                "success": True,
                "message": "Task created successfully",
                "output_data": task_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"Task creation failed: {e}"}
    
    async def _handle_add_tag(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle add tag action"""
        try:
            config = step.config
            tag = config.get("tag")
            
            # Add tag to customer (simulate)
            execution.execution_data.setdefault("tags", []).append(tag)
            
            return {
                "success": True,
                "message": f"Added tag: {tag}",
                "output_data": {"tag": tag}
            }
            
        except Exception as e:
            return {"success": False, "message": f"Tag addition failed: {e}"}
    
    async def _handle_score_update(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle score update action"""
        try:
            config = step.config
            score_type = config.get("score_type")
            score_change = config.get("score_change", 0)
            
            # Update customer score (integrate with lead scoring system)
            score_data = {
                "score_type": score_type,
                "score_change": score_change,
                "customer_id": execution.customer_id
            }
            
            logger.info(f"Updated {score_type} score by {score_change} for {execution.customer_id}")
            
            return {
                "success": True,
                "message": f"Updated {score_type} score",
                "output_data": score_data
            }
            
        except Exception as e:
            return {"success": False, "message": f"Score update failed: {e}"}
    
    async def _handle_branch(self, step: WorkflowStep, execution: WorkflowExecution) -> Dict[str, Any]:
        """Handle branching logic action"""
        try:
            config = step.config
            conditions = config.get("conditions", [])
            branches = config.get("branches", {})
            
            # Evaluate conditions and determine branch
            for condition in conditions:
                if self._evaluate_condition(condition, execution):
                    branch_path = condition.get("branch")
                    return {
                        "success": True,
                        "message": f"Branched to {branch_path}",
                        "branch_path": branch_path,
                        "output_data": {"branch": branch_path}
                    }
            
            # Default branch
            default_branch = branches.get("default")
            return {
                "success": True,
                "message": f"Used default branch: {default_branch}",
                "branch_path": default_branch,
                "output_data": {"branch": default_branch}
            }
            
        except Exception as e:
            return {"success": False, "message": f"Branching failed: {e}"}
    
    def get_workflow_performance(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow performance metrics"""
        try:
            workflow = self.db.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                return {"error": "Workflow not found"}
            
            executions = self.db.query(WorkflowExecution).filter(
                WorkflowExecution.workflow_id == workflow_id
            ).all()
            
            if not executions:
                return {"message": "No executions found"}
            
            # Calculate metrics
            total_executions = len(executions)
            completed_executions = len([e for e in executions if e.status == "completed"])
            failed_executions = len([e for e in executions if e.status == "failed"])
            
            # Completion rate
            completion_rate = (completed_executions / total_executions * 100) if total_executions > 0 else 0
            
            # Average execution time
            completed = [e for e in executions if e.status == "completed" and e.completed_at]
            avg_execution_time = 0
            if completed:
                execution_times = [(e.completed_at - e.started_at).total_seconds() for e in completed]
                avg_execution_time = sum(execution_times) / len(execution_times)
            
            # Step performance
            step_logs = self.db.query(WorkflowStepLog).join(WorkflowExecution).filter(
                WorkflowExecution.workflow_id == workflow_id
            ).all()
            
            step_performance = {}
            for log in step_logs:
                step_name = log.step_name
                if step_name not in step_performance:
                    step_performance[step_name] = {"success": 0, "failed": 0, "skipped": 0}
                step_performance[step_name][log.status] += 1
            
            return {
                "workflow_id": workflow_id,
                "workflow_name": workflow.name,
                "status": workflow.status,
                "execution_metrics": {
                    "total_executions": total_executions,
                    "completed_executions": completed_executions,
                    "failed_executions": failed_executions,
                    "completion_rate": completion_rate,
                    "average_execution_time_seconds": avg_execution_time
                },
                "step_performance": step_performance,
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow performance: {e}")
            return {"error": str(e)}
    
    # Helper methods
    def _validate_workflow_config(self, config: Dict[str, Any]):
        """Validate workflow configuration"""
        required_fields = ["name", "trigger", "steps"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate trigger
        trigger = config["trigger"]
        if "trigger_type" not in trigger:
            raise ValueError("Trigger must have trigger_type")
        
        # Validate steps
        steps = config["steps"]
        if not isinstance(steps, list) or len(steps) == 0:
            raise ValueError("Steps must be a non-empty list")
        
        for step in steps:
            if "action_type" not in step:
                raise ValueError("Each step must have action_type")
    
    def _setup_workflow_triggers(self, workflow: Workflow):
        """Setup trigger monitoring for workflow"""
        trigger_config = workflow.trigger_config
        trigger_type = TriggerType(trigger_config["trigger_type"])
        
        # Setup different trigger types
        if trigger_type == TriggerType.TIME_BASED:
            # Schedule time-based triggers
            pass
        elif trigger_type == TriggerType.BEHAVIOR_BASED:
            # Setup behavior monitoring
            pass
        # Add other trigger types as needed
    
    def _customer_matches_criteria(self, customer_id: str, criteria: Dict[str, Any]) -> bool:
        """Check if customer matches target audience criteria"""
        if not criteria:
            return True
        
        # Get customer data
        customer_data = self._get_customer_data(customer_id)
        if not customer_data:
            return False
        
        # Check criteria
        for field, condition in criteria.items():
            if field not in customer_data:
                return False
            
            customer_value = customer_data[field]
            
            if isinstance(condition, dict):
                operator = condition.get("operator", "equals")
                value = condition.get("value")
                
                if operator == "equals" and customer_value != value:
                    return False
                elif operator == "greater_than" and customer_value <= value:
                    return False
                elif operator == "less_than" and customer_value >= value:
                    return False
                elif operator == "contains" and value not in customer_value:
                    return False
            else:
                if customer_value != condition:
                    return False
        
        return True
    
    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], 
                           execution: WorkflowExecution) -> bool:
        """Evaluate step conditions"""
        if not conditions:
            return True
        
        for condition in conditions:
            if not self._evaluate_condition(condition, execution):
                return False
        
        return True
    
    def _evaluate_condition(self, condition: Dict[str, Any], 
                          execution: WorkflowExecution) -> bool:
        """Evaluate a single condition"""
        condition_type = condition.get("type")
        
        if condition_type == "customer_field":
            customer_data = self._get_customer_data(execution.customer_id)
            field = condition.get("field")
            operator = condition.get("operator", "equals")
            value = condition.get("value")
            
            if field not in customer_data:
                return False
            
            customer_value = customer_data[field]
            
            if operator == "equals":
                return customer_value == value
            elif operator == "greater_than":
                return customer_value > value
            elif operator == "less_than":
                return customer_value < value
            elif operator == "contains":
                return value in customer_value
        
        elif condition_type == "execution_data":
            field = condition.get("field")
            operator = condition.get("operator", "equals")
            value = condition.get("value")
            
            execution_value = execution.execution_data.get(field)
            
            if operator == "equals":
                return execution_value == value
            elif operator == "exists":
                return field in execution.execution_data
        
        return True
    
    def _get_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """Get customer data for personalization and conditions"""
        from core.database import Customer
        customer = self.db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()
        
        if not customer:
            return {}
        
        return {
            "customer_id": customer.customer_id,
            "email": getattr(customer, 'email', ''),
            "phone": getattr(customer, 'phone', ''),
            "age": customer.age,
            "gender": customer.gender,
            "segment_id": customer.segment_id,
            "rating_id": customer.rating_id,
            "created_at": customer.created_at.isoformat() if customer.created_at else None
        }
    
    def _personalize_content(self, content: str, customer_data: Dict[str, Any], 
                           personalization: Dict[str, Any] = None) -> str:
        """Personalize content with customer data"""
        if not content:
            return content
        
        # Replace placeholders
        personalized = content
        for key, value in customer_data.items():
            placeholder = f"{{{key}}}"
            if placeholder in personalized:
                personalized = personalized.replace(placeholder, str(value))
        
        # Apply additional personalization rules
        if personalization:
            for rule_name, rule_config in personalization.items():
                # Apply personalization rules
                pass
        
        return personalized
    
    def _log_step_execution(self, execution_id: str, step_number: int, step_type: str,
                          step_name: str, status: str, message: str = "",
                          execution_time_ms: int = 0, input_data: Dict = None,
                          output_data: Dict = None):
        """Log step execution"""
        log = WorkflowStepLog(
            execution_id=execution_id,
            step_number=step_number,
            step_type=step_type,
            step_name=step_name,
            status=status,
            execution_time_ms=execution_time_ms,
            input_data=input_data or {},
            output_data=output_data or {},
            error_message=message if status == "failed" else None
        )
        
        self.db.add(log)
        self.db.commit()