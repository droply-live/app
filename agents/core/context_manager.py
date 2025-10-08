"""
Context Manager for Agentic Core
Manages context and state across all agents, ensuring coordinated behavior
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

class ContextType(Enum):
    """Types of context that can be managed"""
    RFQ_CONTEXT = "rfq_context"
    ORDER_CONTEXT = "order_context"
    SUPPLIER_CONTEXT = "supplier_context"
    CONTRACT_CONTEXT = "contract_context"
    USER_CONTEXT = "user_context"
    SYSTEM_CONTEXT = "system_context"

@dataclass
class AgentContext:
    """Context for a specific agent"""
    agent_id: str
    context_type: ContextType
    data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

class ContextManager:
    """
    Manages context and state across all agents
    Provides shared memory and coordination between agents
    """
    
    def __init__(self):
        self.contexts: Dict[str, AgentContext] = {}
        self.context_history: List[AgentContext] = []
        
    def create_context(self, agent_id: str, context_type: ContextType, 
                      data: Dict[str, Any], expires_in_hours: Optional[int] = None) -> str:
        """Create a new context for an agent"""
        context_id = f"{agent_id}_{context_type.value}_{datetime.now().timestamp()}"
        
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now(timezone.utc).replace(
                hour=datetime.now(timezone.utc).hour + expires_in_hours
            )
        
        context = AgentContext(
            agent_id=agent_id,
            context_type=context_type,
            data=data,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        
        self.contexts[context_id] = context
        self.context_history.append(context)
        
        return context_id
    
    def get_context(self, context_id: str) -> Optional[AgentContext]:
        """Get context by ID"""
        context = self.contexts.get(context_id)
        
        if context and context.expires_at:
            if datetime.now(timezone.utc) > context.expires_at:
                self.remove_context(context_id)
                return None
                
        return context
    
    def update_context(self, context_id: str, data: Dict[str, Any]) -> bool:
        """Update context data"""
        context = self.contexts.get(context_id)
        if not context:
            return False
            
        context.data.update(data)
        context.updated_at = datetime.now(timezone.utc)
        return True
    
    def remove_context(self, context_id: str) -> bool:
        """Remove context"""
        if context_id in self.contexts:
            del self.contexts[context_id]
            return True
        return False
    
    def get_contexts_by_agent(self, agent_id: str) -> List[AgentContext]:
        """Get all contexts for a specific agent"""
        return [ctx for ctx in self.contexts.values() if ctx.agent_id == agent_id]
    
    def get_contexts_by_type(self, context_type: ContextType) -> List[AgentContext]:
        """Get all contexts of a specific type"""
        return [ctx for ctx in self.contexts.values() if ctx.context_type == context_type]
    
    def get_related_contexts(self, context_id: str) -> List[AgentContext]:
        """Get contexts related to the given context"""
        context = self.get_context(context_id)
        if not context:
            return []
            
        # Find related contexts based on shared data keys
        related = []
        for other_context in self.contexts.values():
            if other_context.context_id != context_id:
                # Check for shared keys that might indicate relationship
                shared_keys = set(context.data.keys()) & set(other_context.data.keys())
                if shared_keys:
                    related.append(other_context)
                    
        return related
    
    def cleanup_expired_contexts(self):
        """Remove expired contexts"""
        now = datetime.now(timezone.utc)
        expired_ids = []
        
        for context_id, context in self.contexts.items():
            if context.expires_at and now > context.expires_at:
                expired_ids.append(context_id)
                
        for context_id in expired_ids:
            self.remove_context(context_id)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of all contexts"""
        return {
            'total_contexts': len(self.contexts),
            'contexts_by_type': {
                ctx_type.value: len(self.get_contexts_by_type(ctx_type))
                for ctx_type in ContextType
            },
            'contexts_by_agent': {
                agent_id: len(self.get_contexts_by_agent(agent_id))
                for agent_id in set(ctx.agent_id for ctx in self.contexts.values())
            }
        }
    
    def export_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Export context as JSON-serializable dict"""
        context = self.get_context(context_id)
        if not context:
            return None
            
        return {
            'context_id': context_id,
            'agent_id': context.agent_id,
            'context_type': context.context_type.value,
            'data': context.data,
            'created_at': context.created_at.isoformat(),
            'updated_at': context.updated_at.isoformat(),
            'expires_at': context.expires_at.isoformat() if context.expires_at else None
        }
    
    def import_context(self, context_data: Dict[str, Any]) -> str:
        """Import context from JSON data"""
        context_id = context_data['context_id']
        
        context = AgentContext(
            agent_id=context_data['agent_id'],
            context_type=ContextType(context_data['context_type']),
            data=context_data['data'],
            created_at=datetime.fromisoformat(context_data['created_at']),
            updated_at=datetime.fromisoformat(context_data['updated_at']),
            expires_at=datetime.fromisoformat(context_data['expires_at']) if context_data['expires_at'] else None
        )
        
        self.contexts[context_id] = context
        return context_id







