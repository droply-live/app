"""
Agent Manager for Agentic Core
Orchestrates all agents and manages their lifecycle
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
import asyncio
import threading
import queue
import logging

from .context_manager import ContextManager, ContextType
from .constants import AGENT_TYPES, AGENT_CAPABILITIES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Status of an agent"""
    IDLE = "idle"
    RUNNING = "running"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"

class AgentEvent(Enum):
    """Events that can trigger agent actions"""
    RFQ_CREATED = "rfq_created"
    RFQ_RESPONSE_RECEIVED = "rfq_response_received"
    ORDER_CREATED = "order_created"
    ORDER_DELAYED = "order_delayed"
    SUPPLIER_UPDATED = "supplier_updated"
    CONTRACT_EXPIRING = "contract_expiring"
    USER_QUERY = "user_query"
    SYSTEM_ALERT = "system_alert"

@dataclass
class AgentTask:
    """Task for an agent to execute"""
    task_id: str
    agent_id: str
    event_type: AgentEvent
    data: Dict[str, Any]
    priority: int = 1  # 1 = highest, 5 = lowest
    created_at: datetime = None
    timeout: Optional[int] = None  # seconds
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

class AgentManager:
    """
    Manages all agents and orchestrates their behavior
    Acts as the central coordinator for the agentic system
    """
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.agent_status: Dict[str, AgentStatus] = {}
        self.context_manager = ContextManager()
        self.task_queue = queue.PriorityQueue()
        self.event_handlers: Dict[AgentEvent, List[str]] = {}
        self.running = False
        self.worker_threads: List[threading.Thread] = []
        
    def register_agent(self, agent_id: str, agent_instance: Any, 
                      capabilities: List[str], event_subscriptions: List[AgentEvent]) -> bool:
        """Register an agent with the manager"""
        try:
            self.agents[agent_id] = agent_instance
            self.agent_status[agent_id] = AgentStatus.IDLE
            
            # Register event handlers
            for event in event_subscriptions:
                if event not in self.event_handlers:
                    self.event_handlers[event] = []
                self.event_handlers[event].append(agent_id)
            
            logger.info(f"Registered agent {agent_id} with capabilities: {capabilities}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.agent_status[agent_id]
            
            # Remove from event handlers
            for event, agents in self.event_handlers.items():
                if agent_id in agents:
                    agents.remove(agent_id)
            
            logger.info(f"Unregistered agent {agent_id}")
            return True
        return False
    
    def start_agent(self, agent_id: str) -> bool:
        """Start a specific agent"""
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found")
            return False
            
        try:
            if hasattr(self.agents[agent_id], 'start'):
                self.agents[agent_id].start()
            self.agent_status[agent_id] = AgentStatus.RUNNING
            logger.info(f"Started agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start agent {agent_id}: {e}")
            self.agent_status[agent_id] = AgentStatus.ERROR
            return False
    
    def stop_agent(self, agent_id: str) -> bool:
        """Stop a specific agent"""
        if agent_id not in self.agents:
            return False
            
        try:
            if hasattr(self.agents[agent_id], 'stop'):
                self.agents[agent_id].stop()
            self.agent_status[agent_id] = AgentStatus.STOPPED
            logger.info(f"Stopped agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {e}")
            return False
    
    def start_all_agents(self) -> bool:
        """Start all registered agents"""
        success_count = 0
        for agent_id in self.agents.keys():
            if self.start_agent(agent_id):
                success_count += 1
        
        logger.info(f"Started {success_count}/{len(self.agents)} agents")
        return success_count == len(self.agents)
    
    def stop_all_agents(self) -> bool:
        """Stop all agents"""
        success_count = 0
        for agent_id in self.agents.keys():
            if self.stop_agent(agent_id):
                success_count += 1
        
        logger.info(f"Stopped {success_count}/{len(self.agents)} agents")
        return success_count == len(self.agents)
    
    def trigger_event(self, event: AgentEvent, data: Dict[str, Any]) -> bool:
        """Trigger an event for subscribed agents"""
        if event not in self.event_handlers:
            logger.warning(f"No agents subscribed to event {event}")
            return False
        
        subscribed_agents = self.event_handlers[event]
        success_count = 0
        
        for agent_id in subscribed_agents:
            if agent_id in self.agents and self.agent_status[agent_id] == AgentStatus.RUNNING:
                try:
                    # Create task for agent
                    task = AgentTask(
                        task_id=f"{event.value}_{datetime.now().timestamp()}",
                        agent_id=agent_id,
                        event_type=event,
                        data=data
                    )
                    
                    # Add to task queue
                    self.task_queue.put((task.priority, task))
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to create task for agent {agent_id}: {e}")
        
        logger.info(f"Triggered event {event} for {success_count}/{len(subscribed_agents)} agents")
        return success_count > 0
    
    def execute_task(self, task: AgentTask) -> bool:
        """Execute a task for an agent"""
        agent_id = task.agent_id
        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} not found for task {task.task_id}")
            return False
        
        try:
            self.agent_status[agent_id] = AgentStatus.BUSY
            
            # Get agent instance
            agent = self.agents[agent_id]
            
            # Create context for the task
            context_id = self.context_manager.create_context(
                agent_id=agent_id,
                context_type=ContextType.SYSTEM_CONTEXT,
                data=task.data,
                expires_in_hours=24
            )
            
            # Execute agent method based on event type
            if hasattr(agent, 'handle_event'):
                result = agent.handle_event(task.event_type, task.data, context_id)
            else:
                logger.error(f"Agent {agent_id} does not have handle_event method")
                return False
            
            # Update context with results
            if result:
                self.context_manager.update_context(context_id, {'result': result})
            
            self.agent_status[agent_id] = AgentStatus.RUNNING
            logger.info(f"Executed task {task.task_id} for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute task {task.task_id} for agent {agent_id}: {e}")
            self.agent_status[agent_id] = AgentStatus.ERROR
            return False
    
    def start_worker_threads(self, num_threads: int = 3):
        """Start worker threads to process tasks"""
        self.running = True
        
        for i in range(num_threads):
            thread = threading.Thread(target=self._worker_loop, name=f"AgentWorker-{i}")
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)
        
        logger.info(f"Started {num_threads} worker threads")
    
    def stop_worker_threads(self):
        """Stop worker threads"""
        self.running = False
        
        for thread in self.worker_threads:
            thread.join(timeout=5)
        
        self.worker_threads.clear()
        logger.info("Stopped worker threads")
    
    def _worker_loop(self):
        """Worker loop for processing tasks"""
        while self.running:
            try:
                # Get task from queue (with timeout)
                priority, task = self.task_queue.get(timeout=1)
                
                # Execute task
                self.execute_task(task)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
    
    def get_agent_status(self, agent_id: str) -> Optional[AgentStatus]:
        """Get status of a specific agent"""
        return self.agent_status.get(agent_id)
    
    def get_all_agent_status(self) -> Dict[str, AgentStatus]:
        """Get status of all agents"""
        return self.agent_status.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'total_agents': len(self.agents),
            'running_agents': len([s for s in self.agent_status.values() if s == AgentStatus.RUNNING]),
            'busy_agents': len([s for s in self.agent_status.values() if s == AgentStatus.BUSY]),
            'error_agents': len([s for s in self.agent_status.values() if s == AgentStatus.ERROR]),
            'queued_tasks': self.task_queue.qsize(),
            'worker_threads': len(self.worker_threads),
            'context_summary': self.context_manager.get_context_summary()
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop_all_agents()
        self.stop_worker_threads()
        self.context_manager.cleanup_expired_contexts()
        logger.info("Agent manager cleanup completed")
