"""
ProcuraAI - Agentic Procurement System
Main integration file that brings together all agents and capabilities
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone

from .core.agent_manager import AgentManager, AgentEvent
from .core.context_manager import ContextManager
from .agents.rfq_agent import RFQAgent
from .agents.order_agent import OrderAgent
from .agents.supplier_agent import SupplierAgent
from .agents.contract_agent import ContractAgent
from .natural_language_interface import NaturalLanguageInterface
from .core.constants import APP_NAME, PRIMARY_COLOR

logger = logging.getLogger(__name__)

class ProcuraAI:
    """
    ProcuraAI - The main agentic procurement system
    Orchestrates all agents and provides the unified interface
    """
    
    def __init__(self):
        self.agent_manager = AgentManager()
        self.context_manager = ContextManager()
        self.natural_language_interface = NaturalLanguageInterface(self.agent_manager)
        
        # Initialize agents
        self.rfq_agent = RFQAgent()
        self.order_agent = OrderAgent()
        self.supplier_agent = SupplierAgent()
        self.contract_agent = ContractAgent()
        
        # Register agents with the manager
        self._register_agents()
        
        # System status
        self.is_initialized = False
        self.startup_time = None
        
        logger.info(f"Initialized {APP_NAME} system")
    
    def _register_agents(self):
        """Register all agents with the agent manager"""
        try:
            # Register RFQ Agent
            self.agent_manager.register_agent(
                agent_id="rfq_agent",
                agent_instance=self.rfq_agent,
                capabilities=[
                    'auto_source_suppliers',
                    'generate_rfq_content',
                    'send_rfq_emails',
                    'parse_quote_responses',
                    'normalize_quote_data',
                    'build_comparison_tables',
                    'recommend_suppliers'
                ],
                event_subscriptions=[
                    AgentEvent.RFQ_CREATED,
                    AgentEvent.RFQ_RESPONSE_RECEIVED,
                    AgentEvent.USER_QUERY
                ]
            )
            
            # Register Order Agent
            self.agent_manager.register_agent(
                agent_id="order_agent",
                agent_instance=self.order_agent,
                capabilities=[
                    'monitor_confirmations',
                    'track_delivery_dates',
                    'escalate_delays',
                    'sync_with_erp',
                    'auto_update_statuses',
                    'chat_with_suppliers',
                    'predict_delays'
                ],
                event_subscriptions=[
                    AgentEvent.ORDER_CREATED,
                    AgentEvent.ORDER_DELAYED,
                    AgentEvent.USER_QUERY
                ]
            )
            
            # Register Supplier Agent
            self.agent_manager.register_agent(
                agent_id="supplier_agent",
                agent_instance=self.supplier_agent,
                capabilities=[
                    'calculate_performance_scores',
                    'flag_anomalies',
                    'suggest_alternatives',
                    'analyze_trends',
                    'monitor_quality',
                    'track_competitiveness'
                ],
                event_subscriptions=[
                    AgentEvent.SUPPLIER_UPDATED,
                    AgentEvent.USER_QUERY
                ]
            )
            
            # Register Contract Agent
            self.agent_manager.register_agent(
                agent_id="contract_agent",
                agent_instance=self.contract_agent,
                capabilities=[
                    'monitor_terms',
                    'track_renewals',
                    'alert_expirations',
                    'propose_renegotiations',
                    'track_consumption',
                    'ensure_compliance'
                ],
                event_subscriptions=[
                    AgentEvent.CONTRACT_EXPIRING,
                    AgentEvent.USER_QUERY
                ]
            )
            
            logger.info("All agents registered successfully")
            
        except Exception as e:
            logger.error(f"Error registering agents: {e}")
            raise
    
    def start(self):
        """Start the ProcuraAI system"""
        try:
            # Start all agents
            self.agent_manager.start_all_agents()
            
            # Start worker threads
            self.agent_manager.start_worker_threads()
            
            # Mark as initialized
            self.is_initialized = True
            self.startup_time = datetime.now(timezone.utc)
            
            logger.info(f"{APP_NAME} system started successfully")
            
        except Exception as e:
            logger.error(f"Error starting {APP_NAME} system: {e}")
            raise
    
    def stop(self):
        """Stop the ProcuraAI system"""
        try:
            # Stop all agents
            self.agent_manager.stop_all_agents()
            
            # Stop worker threads
            self.agent_manager.stop_worker_threads()
            
            # Cleanup
            self.agent_manager.cleanup()
            
            self.is_initialized = False
            
            logger.info(f"{APP_NAME} system stopped")
            
        except Exception as e:
            logger.error(f"Error stopping {APP_NAME} system: {e}")
            raise
    
    def process_natural_language_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a natural language query"""
        try:
            if not self.is_initialized:
                return {'error': 'System not initialized'}
            
            # Process the query through the natural language interface
            result = self.natural_language_interface.process_query(query, user_id)
            
            # Trigger relevant events based on the query
            self._trigger_events_from_query(query, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {'error': str(e)}
    
    def _trigger_events_from_query(self, query: str, result: Dict[str, Any]):
        """Trigger relevant events based on the query"""
        try:
            query_lower = query.lower()
            
            # Check for specific triggers
            if 'rfq' in query_lower or 'quote' in query_lower:
                self.agent_manager.trigger_event(AgentEvent.RFQ_CREATED, {'query': query})
            
            if 'order' in query_lower or 'delivery' in query_lower:
                self.agent_manager.trigger_event(AgentEvent.ORDER_CREATED, {'query': query})
            
            if 'supplier' in query_lower or 'performance' in query_lower:
                self.agent_manager.trigger_event(AgentEvent.SUPPLIER_UPDATED, {'query': query})
            
            if 'contract' in query_lower or 'expiring' in query_lower:
                self.agent_manager.trigger_event(AgentEvent.CONTRACT_EXPIRING, {'query': query})
            
        except Exception as e:
            logger.error(f"Error triggering events from query: {e}")
    
    def create_rfq(self, rfq_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new RFQ"""
        try:
            if not self.is_initialized:
                return {'error': 'System not initialized'}
            
            # Trigger RFQ creation event
            result = self.agent_manager.trigger_event(AgentEvent.RFQ_CREATED, rfq_data)
            
            return {
                'rfq_id': rfq_data.get('rfq_id'),
                'status': 'created',
                'agents_notified': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating RFQ: {e}")
            return {'error': str(e)}
    
    def process_quote_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a quote response"""
        try:
            if not self.is_initialized:
                return {'error': 'System not initialized'}
            
            # Trigger RFQ response event
            result = self.agent_manager.trigger_event(AgentEvent.RFQ_RESPONSE_RECEIVED, response_data)
            
            return {
                'response_id': response_data.get('response_id'),
                'status': 'processed',
                'agents_notified': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing quote response: {e}")
            return {'error': str(e)}
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        try:
            if not self.is_initialized:
                return {'error': 'System not initialized'}
            
            # Trigger order creation event
            result = self.agent_manager.trigger_event(AgentEvent.ORDER_CREATED, order_data)
            
            return {
                'order_id': order_data.get('order_id'),
                'status': 'created',
                'agents_notified': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return {'error': str(e)}
    
    def report_order_delay(self, delay_data: Dict[str, Any]) -> Dict[str, Any]:
        """Report an order delay"""
        try:
            if not self.is_initialized:
                return {'error': 'System not initialized'}
            
            # Trigger order delay event
            result = self.agent_manager.trigger_event(AgentEvent.ORDER_DELAYED, delay_data)
            
            return {
                'order_id': delay_data.get('order_id'),
                'status': 'delay_reported',
                'agents_notified': result,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reporting order delay: {e}")
            return {'error': str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            return {
                'app_name': APP_NAME,
                'primary_color': PRIMARY_COLOR,
                'is_initialized': self.is_initialized,
                'startup_time': self.startup_time.isoformat() if self.startup_time else None,
                'agent_manager_status': self.agent_manager.get_system_status(),
                'context_summary': self.context_manager.get_context_summary(),
                'supported_queries': self.natural_language_interface.get_supported_queries()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status of a specific agent"""
        try:
            status = self.agent_manager.get_agent_status(agent_id)
            if status:
                return {
                    'agent_id': agent_id,
                    'status': status.value,
                    'is_running': status.value == 'running'
                }
            else:
                return {'error': f'Agent {agent_id} not found'}
                
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {'error': str(e)}
    
    def get_all_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            return self.agent_manager.get_all_agent_status()
            
        except Exception as e:
            logger.error(f"Error getting all agent status: {e}")
            return {'error': str(e)}
    
    def get_query_history(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get query history"""
        try:
            return self.natural_language_interface.get_query_history(user_id, limit)
            
        except Exception as e:
            logger.error(f"Error getting query history: {e}")
            return []
    
    def __repr__(self):
        return f"<ProcuraAI(initialized={self.is_initialized}, agents={len(self.agent_manager.agents)})>"








