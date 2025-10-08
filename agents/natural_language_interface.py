"""
Natural Language Interface for Agentic Core
Provides ChatGPT-like interface for procurement queries
"""

from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime, timezone

from .core.agent_manager import AgentManager, AgentEvent
from .core.context_manager import ContextType
from .utils.ai_client import AIClient
from .core.constants import NL_QUERY_PATTERNS

logger = logging.getLogger(__name__)

class NaturalLanguageInterface:
    """
    Natural Language Interface for procurement queries
    Provides ChatGPT-like experience for cross-module insights
    """
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.ai_client = AIClient()
        self.query_history = []
        
        # Query patterns and their handlers
        self.query_handlers = {
            'supplier_performance': self._handle_supplier_performance_query,
            'order_tracking': self._handle_order_tracking_query,
            'contract_management': self._handle_contract_management_query,
            'rfq_analysis': self._handle_rfq_analysis_query,
            'general': self._handle_general_query
        }
    
    def process_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a natural language query"""
        try:
            # Log the query
            self.query_history.append({
                'query': query,
                'user_id': user_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Classify the query
            query_type = self._classify_query(query)
            
            # Get context from relevant agents
            context = self._gather_context(query_type, query)
            
            # Generate response
            response = self._generate_response(query, query_type, context)
            
            # Store the interaction
            interaction = {
                'query': query,
                'query_type': query_type,
                'response': response,
                'context': context,
                'user_id': user_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Processed query: {query[:50]}...")
            return interaction
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {'error': str(e)}
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        try:
            query_lower = query.lower()
            
            # Check for supplier performance queries
            supplier_keywords = ['supplier', 'performance', 'rating', 'score', 'underperforming']
            if any(keyword in query_lower for keyword in supplier_keywords):
                return 'supplier_performance'
            
            # Check for order tracking queries
            order_keywords = ['order', 'delivery', 'delay', 'overdue', 'tracking']
            if any(keyword in query_lower for keyword in order_keywords):
                return 'order_tracking'
            
            # Check for contract management queries
            contract_keywords = ['contract', 'expiring', 'renewal', 'terms', 'agreement']
            if any(keyword in query_lower for keyword in contract_keywords):
                return 'contract_management'
            
            # Check for RFQ analysis queries
            rfq_keywords = ['rfq', 'quote', 'bidding', 'tender', 'proposal']
            if any(keyword in query_lower for keyword in rfq_keywords):
                return 'rfq_analysis'
            
            # Default to general query
            return 'general'
            
        except Exception as e:
            logger.error(f"Error classifying query: {e}")
            return 'general'
    
    def _gather_context(self, query_type: str, query: str) -> Dict[str, Any]:
        """Gather context from relevant agents"""
        try:
            context = {
                'query_type': query_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            # Get context from relevant agents based on query type
            if query_type == 'supplier_performance':
                context.update(self._get_supplier_context())
            elif query_type == 'order_tracking':
                context.update(self._get_order_context())
            elif query_type == 'contract_management':
                context.update(self._get_contract_context())
            elif query_type == 'rfq_analysis':
                context.update(self._get_rfq_context())
            else:
                context.update(self._get_general_context())
            
            return context
            
        except Exception as e:
            logger.error(f"Error gathering context: {e}")
            return {}
    
    def _get_supplier_context(self) -> Dict[str, Any]:
        """Get supplier-related context"""
        try:
            # This would gather data from supplier analytics
            return {
                'suppliers': [
                    {'name': 'Supplier A', 'rating': 4.5, 'status': 'active'},
                    {'name': 'Supplier B', 'rating': 3.8, 'status': 'active'},
                    {'name': 'Supplier C', 'rating': 2.1, 'status': 'underperforming'}
                ],
                'metrics': {
                    'total_suppliers': 3,
                    'active_suppliers': 2,
                    'underperforming_suppliers': 1
                }
            }
        except Exception as e:
            logger.error(f"Error getting supplier context: {e}")
            return {}
    
    def _get_order_context(self) -> Dict[str, Any]:
        """Get order-related context"""
        try:
            # This would gather data from order tracking
            return {
                'orders': [
                    {'id': 'ORD-001', 'status': 'delayed', 'delivery_date': '2024-02-15'},
                    {'id': 'ORD-002', 'status': 'on_time', 'delivery_date': '2024-02-20'},
                    {'id': 'ORD-003', 'status': 'overdue', 'delivery_date': '2024-02-10'}
                ],
                'metrics': {
                    'total_orders': 3,
                    'delayed_orders': 1,
                    'overdue_orders': 1,
                    'on_time_orders': 1
                }
            }
        except Exception as e:
            logger.error(f"Error getting order context: {e}")
            return {}
    
    def _get_contract_context(self) -> Dict[str, Any]:
        """Get contract-related context"""
        try:
            # This would gather data from contract management
            return {
                'contracts': [
                    {'id': 'CNT-001', 'status': 'active', 'expiry_date': '2024-12-31'},
                    {'id': 'CNT-002', 'status': 'expiring', 'expiry_date': '2024-03-15'},
                    {'id': 'CNT-003', 'status': 'expired', 'expiry_date': '2024-01-31'}
                ],
                'metrics': {
                    'total_contracts': 3,
                    'active_contracts': 1,
                    'expiring_contracts': 1,
                    'expired_contracts': 1
                }
            }
        except Exception as e:
            logger.error(f"Error getting contract context: {e}")
            return {}
    
    def _get_rfq_context(self) -> Dict[str, Any]:
        """Get RFQ-related context"""
        try:
            # This would gather data from RFQ analysis
            return {
                'rfqs': [
                    {'id': 'RFQ-001', 'status': 'sent', 'responses': 3},
                    {'id': 'RFQ-002', 'status': 'analyzed', 'responses': 5},
                    {'id': 'RFQ-003', 'status': 'awarded', 'responses': 4}
                ],
                'metrics': {
                    'total_rfqs': 3,
                    'sent_rfqs': 1,
                    'analyzed_rfqs': 1,
                    'awarded_rfqs': 1
                }
            }
        except Exception as e:
            logger.error(f"Error getting RFQ context: {e}")
            return {}
    
    def _get_general_context(self) -> Dict[str, Any]:
        """Get general context"""
        try:
            return {
                'system_status': self.agent_manager.get_system_status(),
                'available_queries': list(self.query_handlers.keys())
            }
        except Exception as e:
            logger.error(f"Error getting general context: {e}")
            return {}
    
    def _generate_response(self, query: str, query_type: str, context: Dict[str, Any]) -> str:
        """Generate a natural language response"""
        try:
            # Use AI to generate response based on query and context
            ai_prompt = f"""
            User Query: {query}
            Query Type: {query_type}
            Context: {json.dumps(context, indent=2)}
            
            Provide a helpful, specific response about the procurement system.
            Include relevant data and actionable insights.
            Be conversational and professional.
            """
            
            response = self.ai_client.generate_response(ai_prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error processing your query: {str(e)}"
    
    def _handle_supplier_performance_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle supplier performance queries"""
        try:
            suppliers = context.get('suppliers', [])
            metrics = context.get('metrics', {})
            
            # Generate specific response about supplier performance
            response = f"""
            Based on the current supplier data:
            
            • Total Suppliers: {metrics.get('total_suppliers', 0)}
            • Active Suppliers: {metrics.get('active_suppliers', 0)}
            • Underperforming Suppliers: {metrics.get('underperforming_suppliers', 0)}
            
            Supplier Performance:
            """
            
            for supplier in suppliers:
                status_emoji = "🟢" if supplier['status'] == 'active' else "🔴"
                response += f"\n{status_emoji} {supplier['name']} - Rating: {supplier['rating']}/5.0"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling supplier performance query: {e}")
            return "I couldn't retrieve supplier performance data at this time."
    
    def _handle_order_tracking_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle order tracking queries"""
        try:
            orders = context.get('orders', [])
            metrics = context.get('metrics', {})
            
            # Generate specific response about order tracking
            response = f"""
            Current Order Status:
            
            • Total Orders: {metrics.get('total_orders', 0)}
            • On Time: {metrics.get('on_time_orders', 0)}
            • Delayed: {metrics.get('delayed_orders', 0)}
            • Overdue: {metrics.get('overdue_orders', 0)}
            
            Order Details:
            """
            
            for order in orders:
                status_emoji = "🟢" if order['status'] == 'on_time' else "🔴"
                response += f"\n{status_emoji} {order['id']} - {order['status'].title()} (Due: {order['delivery_date']})"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling order tracking query: {e}")
            return "I couldn't retrieve order tracking data at this time."
    
    def _handle_contract_management_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle contract management queries"""
        try:
            contracts = context.get('contracts', [])
            metrics = context.get('metrics', {})
            
            # Generate specific response about contract management
            response = f"""
            Contract Status Overview:
            
            • Total Contracts: {metrics.get('total_contracts', 0)}
            • Active: {metrics.get('active_contracts', 0)}
            • Expiring Soon: {metrics.get('expiring_contracts', 0)}
            • Expired: {metrics.get('expired_contracts', 0)}
            
            Contract Details:
            """
            
            for contract in contracts:
                status_emoji = "🟢" if contract['status'] == 'active' else "🟡" if contract['status'] == 'expiring' else "🔴"
                response += f"\n{status_emoji} {contract['id']} - {contract['status'].title()} (Expires: {contract['expiry_date']})"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling contract management query: {e}")
            return "I couldn't retrieve contract management data at this time."
    
    def _handle_rfq_analysis_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle RFQ analysis queries"""
        try:
            rfqs = context.get('rfqs', [])
            metrics = context.get('metrics', {})
            
            # Generate specific response about RFQ analysis
            response = f"""
            RFQ Analysis Summary:
            
            • Total RFQs: {metrics.get('total_rfqs', 0)}
            • Sent: {metrics.get('sent_rfqs', 0)}
            • Analyzed: {metrics.get('analyzed_rfqs', 0)}
            • Awarded: {metrics.get('awarded_rfqs', 0)}
            
            RFQ Details:
            """
            
            for rfq in rfqs:
                status_emoji = "📤" if rfq['status'] == 'sent' else "📊" if rfq['status'] == 'analyzed' else "✅"
                response += f"\n{status_emoji} {rfq['id']} - {rfq['status'].title()} ({rfq['responses']} responses)"
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling RFQ analysis query: {e}")
            return "I couldn't retrieve RFQ analysis data at this time."
    
    def _handle_general_query(self, query: str, context: Dict[str, Any]) -> str:
        """Handle general queries"""
        try:
            system_status = context.get('system_status', {})
            
            response = f"""
            I'm your procurement AI assistant. Here's what I can help you with:
            
            🔍 **Query Types I Support:**
            • Supplier Performance - "Show me underperforming suppliers"
            • Order Tracking - "Find overdue orders"
            • Contract Management - "Show expiring contracts"
            • RFQ Analysis - "Analyze recent quotes"
            
            📊 **System Status:**
            • Active Agents: {system_status.get('running_agents', 0)}
            • Queued Tasks: {system_status.get('queued_tasks', 0)}
            
            Just ask me anything about your procurement system!
            """
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling general query: {e}")
            return "I'm here to help with your procurement queries. What would you like to know?"
    
    def get_query_history(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get query history"""
        try:
            history = self.query_history
            
            if user_id:
                history = [q for q in history if q.get('user_id') == user_id]
            
            return history[-limit:]
            
        except Exception as e:
            logger.error(f"Error getting query history: {e}")
            return []
    
    def get_supported_queries(self) -> List[str]:
        """Get list of supported query patterns"""
        return [
            "Show me suppliers who quoted this month but didn't win any RFQs",
            "Find open POs with overdue delivery by more than 5 days",
            "Show me all expiring contracts in the next 30 days",
            "Which suppliers have the best performance ratings?",
            "What are the current order delays?",
            "Analyze recent RFQ responses and recommend the best supplier"
        ]








