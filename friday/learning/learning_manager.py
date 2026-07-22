import logging
import asyncio
from typing import List, Dict, Any

from friday.learning.experience_models import Experience
from friday.learning.experience_store import ExperienceStore
from friday.learning.experience_index import ExperienceIndex
from friday.learning.experience_ranker import ExperienceRanker
from friday.learning.reflection_engine import ReflectionEngine
from friday.learning.pattern_detector import PatternDetector
from friday.learning.habit_detector import HabitDetector
from friday.learning.preference_learner import PreferenceLearner
from friday.learning.workflow_optimizer import WorkflowOptimizer
from friday.learning.failure_analyzer import FailureAnalyzer
from friday.learning.success_analyzer import SuccessAnalyzer
from friday.learning.feedback_processor import FeedbackProcessor
from friday.learning.knowledge_extractor import KnowledgeExtractor
from friday.learning.learning_metrics import LearningMetrics
from friday.learning.learning_context import LearningContext
from friday.learning.learning_result import LearningResult
from friday.learning.learning_events import (
    LEARNING_REFLECTION_COMPLETED,
    LEARNING_PREFERENCE_UPDATED,
    ReflectionCompletedEvent,
    PreferenceUpdatedEvent
)
from friday.providers.llm.base import LlmProvider
from friday.memory.memory_manager import MemoryManager
from friday.events.event_bus import EventBus
from friday.world.world_manager import WorldManager

logger = logging.getLogger(__name__)

class LearningManager:
    """Facade coordinating all learning, pattern detection, and reflection operations."""
    
    def __init__(self,
                 llm_provider: LlmProvider,
                 memory_manager: MemoryManager,
                 world_manager: WorldManager,
                 event_bus: EventBus):
        self.store = ExperienceStore(memory_manager)
        self.index = ExperienceIndex(self.store)
        self.ranker = ExperienceRanker()
        
        self.reflection_engine = ReflectionEngine(llm_provider, self.store)
        self.pattern_detector = PatternDetector(self.store)
        self.habit_detector = HabitDetector(self.store)
        self.preference_learner = PreferenceLearner(self.store)
        self.workflow_optimizer = WorkflowOptimizer()
        self.failure_analyzer = FailureAnalyzer()
        self.success_analyzer = SuccessAnalyzer()
        self.feedback_processor = FeedbackProcessor()
        self.knowledge_extractor = KnowledgeExtractor()
        
        self.world = world_manager
        self.events = event_bus
        
    async def log_experience(self, experience: Experience):
        """Logs a raw experience into the store."""
        await self.store.add_experience(experience)
        
    async def run_reflection_cycle(self, context: LearningContext) -> LearningResult:
        """Runs the periodic reflection and learning cycle."""
        metrics = LearningMetrics(session_id=context.session_id)
        metrics.start()
        
        try:
            recent_exps = await self.store.get_recent_experiences(50)
            
            # Run all analysis in parallel
            results = await asyncio.gather(
                self.reflection_engine.reflect_on_experiences(recent_exps),
                self.pattern_detector.detect_patterns(),
                self.habit_detector.detect_habits(),
                self.preference_learner.learn_preferences(),
                self.failure_analyzer.analyze([e for e in recent_exps if not e.success]),
                self.success_analyzer.analyze([e for e in recent_exps if e.success]),
                self.workflow_optimizer.optimize_workflows(recent_exps),
                self.knowledge_extractor.extract_knowledge(recent_exps),
                return_exceptions=True
            )
            
            # Map results
            lessons = results[0] if not isinstance(results[0], Exception) else []
            patterns = results[1] if not isinstance(results[1], Exception) else []
            habits = results[2] if not isinstance(results[2], Exception) else []
            prefs = results[3] if not isinstance(results[3], Exception) else {}
            failures = results[4] if not isinstance(results[4], Exception) else []
            successes = results[5] if not isinstance(results[5], Exception) else []
            opts = results[6] if not isinstance(results[6], Exception) else []
            know = results[7] if not isinstance(results[7], Exception) else []
            
            # Publish and Apply
            await self._apply_preferences(prefs, context.session_id)
            await self._update_world_model(habits)
            
            all_insights = lessons + patterns + failures + successes + opts + know
            
            if all_insights:
                from dataclasses import asdict
                await self.events.publish(LEARNING_REFLECTION_COMPLETED, 
                                        asdict(ReflectionCompletedEvent(
                                            event_type=LEARNING_REFLECTION_COMPLETED,
                                            session_id=context.session_id,
                                            source=context.trigger_source,
                                            insights=all_insights
                                        )))
                
            metrics.end()
            return LearningResult(
                success=True,
                insights_generated=all_insights,
                patterns_detected=len(patterns),
                preferences_updated=len(prefs),
                workflows_optimized=len(opts),
                duration_ms=metrics.duration_ms
            )
            
        except Exception as e:
            logger.error(f"Reflection cycle failed: {e}")
            metrics.end()
            return LearningResult(success=False, error=str(e), duration_ms=metrics.duration_ms)

    async def _apply_preferences(self, prefs: Dict[str, Any], session_id: str):
        from dataclasses import asdict
        for k, v in prefs.items():
            await self.events.publish(LEARNING_PREFERENCE_UPDATED,
                                      asdict(PreferenceUpdatedEvent(
                                          event_type=LEARNING_PREFERENCE_UPDATED,
                                          session_id=session_id,
                                          category=k,
                                          value=v
                                      )))

    async def _update_world_model(self, habits: List[str]):
        """Pushes user habits into the World Model."""
        if habits and hasattr(self.world, "update_state"):
            self.world.update_state("habits", {"detected_habits": habits})
