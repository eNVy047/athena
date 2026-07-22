import uuid
from typing import Dict, Any, List
from friday.core.cognition.models import Plan, Task, ExecutionStep

class Planner:
    """Transforms abstract goals into a Directed Acyclic Graph (DAG) Plan."""
    def __init__(self):
        pass

    async def generate_plan(self, goal_id: str, goal_description: str, context: Dict[str, Any]) -> Plan:
        # Default simple plan generator (acts as placeholder for dynamic LLM-based DAG construction)
        tasks: Dict[str, Task] = {}
        
        # Determine standard tasks based on keywords in goal description
        if "download" in goal_description.lower():
            # Step A: Download
            download_step = ExecutionStep(id=f"step_{uuid.uuid4().hex[:6]}", action_name="os.download", parameters={"query": goal_description})
            tasks["task_download"] = Task(
                id="task_download",
                name="Download Sales Report",
                steps=[download_step],
                dependencies=[]
            )
            # Step B: Summarize (Depends on Download)
            summary_step = ExecutionStep(id=f"step_{uuid.uuid4().hex[:6]}", action_name="nlp.summarize")
            tasks["task_summarize"] = Task(
                id="task_summarize",
                name="Summarize Sales Report",
                steps=[summary_step],
                dependencies=["task_download"]
            )
            # Step C: Send Email (Depends on Summarize)
            email_step = ExecutionStep(id=f"step_{uuid.uuid4().hex[:6]}", action_name="email.send", sensitive=True)
            tasks["task_email"] = Task(
                id="task_email",
                name="Email Summary",
                steps=[email_step],
                dependencies=["task_summarize"]
            )
        else:
            # Default fallback single task
            step = ExecutionStep(id=f"step_{uuid.uuid4().hex[:6]}", action_name="os.default", parameters={"description": goal_description})
            tasks["task_default"] = Task(
                id="task_default",
                name="Default Task Exec",
                steps=[step],
                dependencies=[]
            )

        return Plan(
            id=str(uuid.uuid4()),
            goal_id=goal_id,
            tasks=tasks
        )
