from typing import List
from friday.core.cognition.models import Plan, Reflection, TaskStatus

class ReflectionEngine:
    """Analyzes execution successes and failures to draw behavioral lessons."""
    def __init__(self):
        pass

    async def reflect(self, plan: Plan) -> Reflection:
        lessons = []
        successes = []
        mistakes = []
        
        for tid, task in plan.tasks.items():
            if task.status == TaskStatus.COMPLETED:
                successes.append(f"Successfully completed task: {task.name}")
            elif task.status == TaskStatus.FAILED:
                mistakes.append(f"Failed task: {task.name} with step errors.")
                lessons.append(f"Verify step parameters and action handler bindings for {task.name}")
                
        if not mistakes:
            lessons.append("Plan executed flawlessly. Maintain current action structures.")
            
        reflection = Reflection(
            lessons_learned=lessons,
            success_insights=successes,
            mistakes_identified=mistakes
        )
        
        # Bridge to new Learning Engine if available
        if hasattr(self, "learning_manager") and self.learning_manager:
            from friday.learning.experience_models import Experience
            from friday.learning.learning_context import LearningContext
            import asyncio
            
            exp = Experience(
                id=f"plan_exec_{plan.id}" if hasattr(plan, 'id') else "plan_exec",
                type="workflow",
                trigger="cognition_reflection",
                success=len(mistakes) == 0,
                lessons_learned=lessons
            )
            # Create a fire-and-forget task to log it
            asyncio.create_task(self.learning_manager.log_experience(exp))
            
        return reflection
