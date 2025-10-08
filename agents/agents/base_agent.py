"""
Base Agent Class
All agents inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import Enum
import logging

from ..core.context_manager import ContextManager, ContextType
from ..core.agent_manager import AgentEvent
from ..utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class AgentCapability(Enum):
    """Capabilities that agents can have"""
    AUTO_SOURCE = "auto_source"
    GENERATE_CONTENT = "generate_content"
    SEND_EMAILS = "send_emails"
    PARSE_RESPONSES = "parse_responses"
    NORMALIZE_DATA = "normalize_data"
    BUILD_COMPARISONS = "build_comparisons"
    RECOMMEND = "recommend"
    MONITOR = "monitor"
    TRACK = "track"
    ESCALATE = "escalate"
    SYNC = "sync"
    UPDATE = "update"
    CHAT = "chat"
    PREDICT = "predict"
    CALCULATE = "calculate"
    FLAG = "flag"
    SUGGEST = "suggest"
    ANALYZE = "analyze"
    ALERT = "alert"
    PROPOSE = "propose"
    ENSURE = "ensure"

class BaseAgent(ABC):
    """
    Base class for all agents
    Provides common functionality and interface
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.context_manager = ContextManager()
        self.ai_client = AIClient()
        self.is_running = False
        self.last_activity = None
        
        # Agent configuration
        self.config = {
            'max_concurrent_tasks': 5,
            'task_timeout': 300,  # 5 minutes
            'retry_attempts': 3,
            'log_level': 'INFO'
        }
        
        logger.info(f"Initialized {self.agent_type} agent: {self.agent_id}")
    
    @abstractmethod
    def handle_event(self, event: AgentEvent, data: Dict[str, Any], context_id: str) -> Any:
        """Handle an event - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of agent capabilities"""
        pass
    
    def start(self):
        """Start the agent"""
        self.is_running = True
        self.last_activity = datetime.now(timezone.utc)
        logger.info(f"Started agent {self.agent_id}")
    
    def stop(self):
        """Stop the agent"""
        self.is_running = False
        logger.info(f"Stopped agent {self.agent_id}")
    
    def is_capable_of(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities
    
    def can_handle_event(self, event: AgentEvent) -> bool:
        """Check if agent can handle a specific event"""
        # This should be overridden by subclasses
        return True
    
    def create_context(self, context_type: ContextType, data: Dict[str, Any], 
                      expires_in_hours: Optional[int] = None) -> str:
        """Create a new context"""
        return self.context_manager.create_context(
            agent_id=self.agent_id,
            context_type=context_type,
            data=data,
            expires_in_hours=expires_in_hours
        )
    
    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get context data"""
        context = self.context_manager.get_context(context_id)
        return context.data if context else None
    
    def update_context(self, context_id: str, data: Dict[str, Any]) -> bool:
        """Update context data"""
        return self.context_manager.update_context(context_id, data)
    
    def log_activity(self, activity: str, data: Optional[Dict[str, Any]] = None):
        """Log agent activity"""
        self.last_activity = datetime.now(timezone.utc)
        log_data = {
            'agent_id': self.agent_id,
            'activity': activity,
            'timestamp': self.last_activity.isoformat(),
            'data': data or {}
        }
        logger.info(f"Agent {self.agent_id}: {activity}", extra=log_data)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'is_running': self.is_running,
            'capabilities': [cap.value for cap in self.capabilities],
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'config': self.config
        }
    
    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that data contains required fields"""
        return all(field in data for field in required_fields)
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """Handle errors consistently"""
        error_data = {
            'agent_id': self.agent_id,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        logger.error(f"Agent {self.agent_id} error: {error}", extra=error_data)
    
    def __repr__(self):
        return f"<{self.agent_type}Agent(id={self.agent_id}, capabilities={len(self.capabilities)})>"







