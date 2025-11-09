"""
Trace Logger for observability - logs all events to trace.jsonl
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class TraceLogger:
    """
    Thread-safe logger for structured observability traces in JSONL format.
    Logs every step, message, tool call, and key decision to trace.jsonl.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self, trace_file: str = "trace.jsonl"):
        """
        Initialize the trace logger.
        
        :param trace_file: Path to the JSONL trace file
        """
        self.trace_file = Path(trace_file)
        self.file_handle = None
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialize or clear the trace file."""
        # Create new file (overwrite if exists)
        with open(self.trace_file, 'w') as f:
            pass  # Just create/clear the file
    
    def _write_event(self, event: Dict[str, Any]):
        """
        Write a single event to the trace file.
        
        :param event: Dictionary containing event data
        """
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = datetime.now().isoformat()
        
        # Write as single line of JSON
        with self._lock:
            with open(self.trace_file, 'a') as f:
                f.write(json.dumps(event, default=str) + '\n')
    
    def log_workflow_start(self, config: Dict[str, Any]):
        """Log the start of the workflow."""
        self._write_event({
            'event': 'workflow_start',
            'config': config
        })
    
    def log_workflow_complete(self, output_file: str, success: bool = True):
        """Log the completion of the workflow."""
        self._write_event({
            'event': 'workflow_complete',
            'output_file': output_file,
            'success': success
        })
    
    def log_agent_init(self, agent_name: str, params: Optional[Dict[str, Any]] = None):
        """Log agent initialization."""
        event = {
            'event': 'agent_init',
            'agent': agent_name
        }
        if params:
            event['params'] = params
        self._write_event(event)
    
    def log_agent_action(self, agent_name: str, action: str, details: Optional[Dict[str, Any]] = None):
        """Log an agent action."""
        event = {
            'event': 'agent_action',
            'agent': agent_name,
            'action': action
        }
        if details:
            event['details'] = details
        self._write_event(event)
    
    def log_llm_request(self, agent_name: str, model: str, prompt: str, 
                       temperature: float, seed: int, max_tokens: Optional[int] = None):
        """Log an LLM API request."""
        event = {
            'event': 'llm_request',
            'agent': agent_name,
            'model': model,
            'prompt_preview': prompt[:200] + '...' if len(prompt) > 200 else prompt,
            'prompt_length': len(prompt),
            'temperature': temperature,
            'seed': seed
        }
        if max_tokens:
            event['max_tokens'] = max_tokens
        self._write_event(event)
    
    def log_llm_response(self, agent_name: str, response: str, 
                        tokens: Optional[Dict[str, int]] = None,
                        system_fingerprint: Optional[str] = None):
        """Log an LLM API response."""
        event = {
            'event': 'llm_response',
            'agent': agent_name,
            'response_preview': response[:200] + '...' if len(response) > 200 else response,
            'response_length': len(response)
        }
        if tokens:
            event['tokens'] = tokens
        if system_fingerprint:
            event['system_fingerprint'] = system_fingerprint
        self._write_event(event)
    
    def log_tool_call(self, agent_name: str, tool_name: str, 
                     arguments: Dict[str, Any], result: Optional[str] = None):
        """Log a tool call."""
        event = {
            'event': 'tool_call',
            'agent': agent_name,
            'tool': tool_name,
            'arguments': arguments
        }
        if result:
            event['result_preview'] = result[:200] + '...' if len(result) > 200 else result
            event['result_length'] = len(result)
        self._write_event(event)
    
    def log_decision(self, agent_name: str, decision: str, reason: Optional[str] = None,
                    context: Optional[Dict[str, Any]] = None):
        """Log a key decision made by an agent."""
        event = {
            'event': 'decision',
            'agent': agent_name,
            'decision': decision
        }
        if reason:
            event['reason'] = reason
        if context:
            event['context'] = context
        self._write_event(event)
    
    def log_error(self, agent_name: str, error: str, error_type: Optional[str] = None,
                 traceback: Optional[str] = None):
        """Log an error."""
        event = {
            'event': 'error',
            'agent': agent_name,
            'error': error
        }
        if error_type:
            event['error_type'] = error_type
        if traceback:
            event['traceback'] = traceback
        self._write_event(event)
    
    def log_pdf_operation(self, agent_name: str, operation: str, pdf_path: str,
                         success: bool = True, error: Optional[str] = None):
        """Log a PDF-related operation."""
        event = {
            'event': 'pdf_operation',
            'agent': agent_name,
            'operation': operation,
            'pdf_path': pdf_path,
            'success': success
        }
        if error:
            event['error'] = error
        self._write_event(event)
    
    def log_memory_operation(self, operation: str, thread_id: str, 
                            message: str, sender: Optional[str] = None):
        """Log a memory operation."""
        event = {
            'event': 'memory_operation',
            'operation': operation,
            'thread_id': thread_id,
            'message': message
        }
        if sender:
            event['sender'] = sender
        self._write_event(event)
    
    def log_custom(self, event_type: str, **kwargs):
        """Log a custom event."""
        event = {
            'event': event_type,
            **kwargs
        }
        self._write_event(event)


# Singleton pattern
_global_trace_logger: Optional[TraceLogger] = None


def get_trace_logger(trace_file: str = "trace.jsonl") -> TraceLogger:
    """
    Get or create the global trace logger instance.
    
    :param trace_file: Path to the trace file (only used on first call)
    :return: TraceLogger instance
    """
    global _global_trace_logger
    if _global_trace_logger is None:
        _global_trace_logger = TraceLogger(trace_file)
    return _global_trace_logger
