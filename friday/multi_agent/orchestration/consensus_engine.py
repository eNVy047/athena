from typing import List
from friday.multi_agent.agent_result import AgentResult

class ConsensusEngine:
    """Merges outputs and resolves conflicting agent conclusions."""
    
    def resolve_conflicts(self, results: List[AgentResult]) -> AgentResult:
        if not results:
            return AgentResult(success=False, message="No results to resolve")
            
        success_count = sum(1 for r in results if r.success)
        
        # Simple majority consensus
        if success_count >= len(results) / 2:
            return AgentResult(
                success=True, 
                message="Consensus reached (Success)",
                data={"results_processed": len(results)}
            )
        else:
            return AgentResult(
                success=False, 
                message="Consensus failed (Majority failed)"
            )
