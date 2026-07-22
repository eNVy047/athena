import uuid
from typing import Optional, Dict
from contextlib import contextmanager

class TraceContext:
    def __init__(self, trace_id: str, request_id: str, session_id: str, workflow_id: Optional[str] = None):
        self.trace_id = trace_id
        self.request_id = request_id
        self.session_id = session_id
        self.workflow_id = workflow_id
        self.spans: Dict[str, 'Span'] = {}

class Span:
    def __init__(self, name: str, parent: Optional['Span'] = None):
        self.name = name
        self.parent = parent
        self.span_id = str(uuid.uuid4())
        
class Tracer:
    """Tracks execution path."""
    
    def __init__(self):
        self.current_context: Optional[TraceContext] = None
        self.current_span: Optional[Span] = None
        
    def start_trace(self, request_id: str, session_id: str, workflow_id: Optional[str] = None) -> TraceContext:
        trace_id = str(uuid.uuid4())
        self.current_context = TraceContext(trace_id, request_id, session_id, workflow_id)
        return self.current_context
        
    @contextmanager
    def span(self, name: str):
        span = Span(name, parent=self.current_span)
        prev_span = self.current_span
        self.current_span = span
        if self.current_context:
            self.current_context.spans[span.span_id] = span
        try:
            yield span
        finally:
            self.current_span = prev_span

global_tracer = Tracer()
