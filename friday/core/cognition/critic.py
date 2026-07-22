from typing import List
from friday.core.cognition.models import Plan, Evaluation, TaskStatus

class Critic:
    """Evaluates task execution reports for efficiency and correctness."""
    def __init__(self):
        pass

    async def evaluate_execution(self, plan: Plan) -> Evaluation:
        failed_tasks = [t for t in plan.tasks.values() if t.status == TaskStatus.FAILED]
        success = len(failed_tasks) == 0
        
        # Calculate metric efficiency score
        total_tasks = len(plan.tasks)
        efficiency = (total_tasks - len(failed_tasks)) / total_tasks if total_tasks > 0 else 1.0
        
        report = f"Plan completed. Success={success}. Total tasks={total_tasks}, Failed={len(failed_tasks)}."
        return Evaluation(
            success=success,
            efficiency_score=efficiency,
            report=report,
            retry_recommended=not success
        )
