"""
Marketing Automation API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...automation.workflow_engine import WorkflowEngine, WorkflowStatus

router = APIRouter()

class CreateWorkflowRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    trigger: Dict[str, Any]
    steps: List[Dict[str, Any]]
    target_audience: Optional[Dict[str, Any]] = {}

class TriggerWorkflowRequest(BaseModel):
    customer_id: str
    trigger_data: Optional[Dict[str, Any]] = {}

class WorkflowResponse(BaseModel):
    success: bool
    workflow_id: Optional[str] = None
    message: str

@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: CreateWorkflowRequest,
    current_user: dict = Depends(require_permission("create_campaigns")),
    db: Session = Depends(get_db)
):
    """Create a new marketing workflow"""
    try:
        workflow_engine = WorkflowEngine(db)
        
        workflow_config = {
            "name": request.name,
            "description": request.description,
            "trigger": request.trigger,
            "steps": request.steps,
            "target_audience": request.target_audience,
            "created_by": current_user.get("username", "unknown")
        }
        
        workflow_id = workflow_engine.create_workflow(workflow_config)
        
        return WorkflowResponse(
            success=True,
            workflow_id=workflow_id,
            message="Workflow created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workflow: {str(e)}")

@router.post("/workflows/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    current_user: dict = Depends(require_permission("manage_campaigns")),
    db: Session = Depends(get_db)
):
    """Start (activate) a workflow"""
    try:
        workflow_engine = WorkflowEngine(db)
        success = workflow_engine.start_workflow(workflow_id)
        
        if success:
            return {"success": True, "message": "Workflow started successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to start workflow")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start workflow: {str(e)}")

@router.post("/workflows/{workflow_id}/trigger")
async def trigger_workflow_for_customer(
    workflow_id: str,
    request: TriggerWorkflowRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger a workflow for a specific customer"""
    try:
        workflow_engine = WorkflowEngine(db)
        execution_id = workflow_engine.trigger_workflow(
            workflow_id=workflow_id,
            customer_id=request.customer_id,
            trigger_data=request.trigger_data
        )
        
        if execution_id:
            return {
                "success": True,
                "execution_id": execution_id,
                "message": "Workflow triggered successfully"
            }
        else:
            return {
                "success": False,
                "message": "Customer doesn't match workflow criteria"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger workflow: {str(e)}")

@router.get("/workflows")
async def list_workflows(
    status: Optional[WorkflowStatus] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workflows with optional status filter"""
    try:
        from ...automation.workflow_engine import Workflow
        
        query = db.query(Workflow)
        if status:
            query = query.filter(Workflow.status == status.value)
        
        workflows = query.order_by(Workflow.created_at.desc()).all()
        
        workflow_list = []
        for workflow in workflows:
            workflow_list.append({
                "id": workflow.id,
                "name": workflow.name,
                "description": workflow.description,
                "status": workflow.status,
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "trigger_type": workflow.trigger_config.get("trigger_type"),
                "total_steps": len(workflow.workflow_config.get("steps", []))
            })
        
        return {
            "workflows": workflow_list,
            "total_count": len(workflow_list)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")

@router.get("/workflows/{workflow_id}")
async def get_workflow_details(
    workflow_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed workflow information"""
    try:
        from ...automation.workflow_engine import Workflow
        
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status,
            "trigger_config": workflow.trigger_config,
            "workflow_config": workflow.workflow_config,
            "target_audience": workflow.target_audience,
            "performance_metrics": workflow.performance_metrics,
            "created_by": workflow.created_by,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow details: {str(e)}")

@router.get("/workflows/{workflow_id}/performance")
async def get_workflow_performance(
    workflow_id: str,
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get workflow performance metrics"""
    try:
        workflow_engine = WorkflowEngine(db)
        performance = workflow_engine.get_workflow_performance(workflow_id)
        
        return performance
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow performance: {str(e)}")

@router.get("/workflows/{workflow_id}/executions")
async def get_workflow_executions(
    workflow_id: str,
    limit: int = Query(50, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get workflow execution history"""
    try:
        from ...automation.workflow_engine import WorkflowExecution
        
        query = db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        )
        
        if status:
            query = query.filter(WorkflowExecution.status == status)
        
        executions = query.order_by(
            WorkflowExecution.started_at.desc()
        ).offset(offset).limit(limit).all()
        
        execution_list = []
        for execution in executions:
            execution_list.append({
                "id": execution.id,
                "customer_id": execution.customer_id,
                "status": execution.status,
                "current_step": execution.current_step,
                "started_at": execution.started_at.isoformat(),
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "error_message": execution.error_message,
                "execution_data": execution.execution_data
            })
        
        # Get total count for pagination
        total_count = db.query(WorkflowExecution).filter(
            WorkflowExecution.workflow_id == workflow_id
        ).count()
        
        return {
            "executions": execution_list,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get workflow executions: {str(e)}")

@router.get("/workflows/{workflow_id}/executions/{execution_id}/logs")
async def get_execution_step_logs(
    workflow_id: str,
    execution_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed step logs for a workflow execution"""
    try:
        from ...automation.workflow_engine import WorkflowStepLog, WorkflowExecution
        
        # Verify execution belongs to workflow
        execution = db.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id,
            WorkflowExecution.workflow_id == workflow_id
        ).first()
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        step_logs = db.query(WorkflowStepLog).filter(
            WorkflowStepLog.execution_id == execution_id
        ).order_by(WorkflowStepLog.step_number).all()
        
        logs = []
        for log in step_logs:
            logs.append({
                "step_number": log.step_number,
                "step_type": log.step_type,
                "step_name": log.step_name,
                "status": log.status,
                "executed_at": log.executed_at.isoformat(),
                "execution_time_ms": log.execution_time_ms,
                "input_data": log.input_data,
                "output_data": log.output_data,
                "error_message": log.error_message
            })
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "customer_id": execution.customer_id,
            "step_logs": logs,
            "total_steps": len(logs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get execution logs: {str(e)}")

@router.delete("/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: dict = Depends(require_permission("manage_campaigns")),
    db: Session = Depends(get_db)
):
    """Delete a workflow (admin only)"""
    try:
        from ...automation.workflow_engine import Workflow
        
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Check if workflow is active
        if workflow.status == WorkflowStatus.ACTIVE.value:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete active workflow. Stop it first."
            )
        
        db.delete(workflow)
        db.commit()
        
        return {"success": True, "message": "Workflow deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")

@router.get("/analytics/automation-overview")
async def get_automation_overview(
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get overall automation analytics"""
    try:
        from ...automation.workflow_engine import Workflow, WorkflowExecution
        
        # Workflow statistics
        total_workflows = db.query(Workflow).count()
        active_workflows = db.query(Workflow).filter(
            Workflow.status == WorkflowStatus.ACTIVE.value
        ).count()
        
        # Execution statistics
        total_executions = db.query(WorkflowExecution).count()
        completed_executions = db.query(WorkflowExecution).filter(
            WorkflowExecution.status == "completed"
        ).count()
        failed_executions = db.query(WorkflowExecution).filter(
            WorkflowExecution.status == "failed"
        ).count()
        
        # Recent executions (last 7 days)
        recent_executions = db.query(WorkflowExecution).filter(
            WorkflowExecution.started_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Success rate
        success_rate = (completed_executions / total_executions * 100) if total_executions > 0 else 0
        
        return {
            "workflow_metrics": {
                "total_workflows": total_workflows,
                "active_workflows": active_workflows,
                "draft_workflows": total_workflows - active_workflows
            },
            "execution_metrics": {
                "total_executions": total_executions,
                "completed_executions": completed_executions,
                "failed_executions": failed_executions,
                "success_rate": success_rate,
                "recent_executions_7d": recent_executions
            },
            "performance_indicators": {
                "automation_adoption": (active_workflows / max(1, total_workflows)) * 100,
                "execution_velocity": recent_executions / 7,  # Avg executions per day
                "failure_rate": (failed_executions / max(1, total_executions)) * 100
            },
            "recommendations": _generate_automation_recommendations(
                total_workflows, active_workflows, success_rate
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get automation overview: {str(e)}")

def _generate_automation_recommendations(total_workflows: int, active_workflows: int, 
                                       success_rate: float) -> List[str]:
    """Generate automation recommendations based on metrics"""
    recommendations = []
    
    if total_workflows == 0:
        recommendations.append("Start by creating your first marketing automation workflow")
    elif active_workflows == 0:
        recommendations.append("Activate your workflows to start automation benefits")
    elif active_workflows / total_workflows < 0.5:
        recommendations.append("Consider activating more workflows to increase automation coverage")
    
    if success_rate < 80:
        recommendations.append("Review and optimize failing workflow steps")
    elif success_rate > 95:
        recommendations.append("Excellent automation performance - consider expanding to new use cases")
    
    if total_workflows < 5:
        recommendations.append("Explore additional automation opportunities like welcome series and re-engagement")
    
    return recommendations