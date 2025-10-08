"""
Order Agent - Follow-Up & Delay Tracker
Monitors orders, tracks delivery, handles delays, and syncs with ERP
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
import json
import logging

from .base_agent import BaseAgent, AgentCapability
from ..core.agent_manager import AgentEvent
from ..core.context_manager import ContextType
from ..utils.ai_client import AIClient
from ..utils.erp_sync import ERPSync
from ..core.constants import EMAIL_TEMPLATES, STATUS_ENUMS

logger = logging.getLogger(__name__)

class OrderAgent(BaseAgent):
    """
    Order Agent - Follow-Up & Delay Tracker
    
    Capabilities:
    - Monitor supplier confirmations and delivery dates
    - Track and escalate delays automatically
    - Sync with ERP systems
    - Auto-update order statuses
    - Chat with suppliers about delays
    - Predict delivery delays using historical data
    """
    
    def __init__(self, agent_id: str = "order_agent"):
        capabilities = [
            AgentCapability.MONITOR,
            AgentCapability.TRACK,
            AgentCapability.ESCALATE,
            AgentCapability.SYNC,
            AgentCapability.UPDATE,
            AgentCapability.CHAT,
            AgentCapability.PREDICT
        ]
        
        super().__init__(agent_id, "Order", capabilities)
        self.erp_sync = ERPSync()
        
        # Order-specific configuration
        self.config.update({
            'delay_threshold_hours': 24,
            'escalation_levels': 3,
            'auto_sync_interval': 3600,  # 1 hour
            'prediction_window_days': 7,
            'chat_enabled': True
        })
    
    def handle_event(self, event: AgentEvent, data: Dict[str, Any], context_id: str) -> Any:
        """Handle order-related events"""
        try:
            self.log_activity(f"Handling event: {event.value}", data)
            
            if event == AgentEvent.ORDER_CREATED:
                return self._process_new_order(data, context_id)
            elif event == AgentEvent.ORDER_DELAYED:
                return self._handle_order_delay(data, context_id)
            elif event == AgentEvent.USER_QUERY:
                return self._handle_user_query(data, context_id)
            else:
                logger.warning(f"Unhandled event type: {event}")
                return None
                
        except Exception as e:
            self.handle_error(e, f"handle_event for {event.value}")
            return None
    
    def _process_new_order(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Process a new order and set up monitoring"""
        try:
            # Validate required fields
            required_fields = ['order_id', 'supplier_id', 'delivery_date', 'items']
            if not self.validate_data(data, required_fields):
                raise ValueError("Missing required order fields")
            
            # Set up order monitoring
            monitoring_config = self._setup_order_monitoring(data)
            
            # Sync with ERP
            erp_sync_result = self._sync_order_with_erp(data)
            
            # Create context for order tracking
            order_context = {
                'order_id': data['order_id'],
                'supplier_id': data['supplier_id'],
                'delivery_date': data['delivery_date'],
                'status': 'pending_confirmation',
                'monitoring_config': monitoring_config,
                'erp_sync': erp_sync_result,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            self.update_context(context_id, order_context)
            self.log_activity("New order processed and monitoring setup", order_context)
            
            return order_context
            
        except Exception as e:
            self.handle_error(e, "process_new_order")
            return {'error': str(e)}
    
    def _setup_order_monitoring(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Set up monitoring configuration for an order"""
        try:
            delivery_date = datetime.fromisoformat(order_data['delivery_date'].replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            # Calculate monitoring checkpoints
            checkpoints = []
            
            # 50% of lead time
            mid_point = now + (delivery_date - now) / 2
            checkpoints.append({
                'name': 'mid_point_check',
                'datetime': mid_point.isoformat(),
                'action': 'check_progress'
            })
            
            # 1 week before delivery
            week_before = delivery_date - timedelta(days=7)
            if week_before > now:
                checkpoints.append({
                    'name': 'week_before_check',
                    'datetime': week_before.isoformat(),
                    'action': 'confirm_delivery'
                })
            
            # Day before delivery
            day_before = delivery_date - timedelta(days=1)
            if day_before > now:
                checkpoints.append({
                    'name': 'day_before_check',
                    'datetime': day_before.isoformat(),
                    'action': 'final_confirmation'
                })
            
            return {
                'checkpoints': checkpoints,
                'delay_threshold_hours': self.config['delay_threshold_hours'],
                'escalation_enabled': True,
                'auto_sync_enabled': True
            }
            
        except Exception as e:
            self.handle_error(e, "setup_order_monitoring")
            return {}
    
    def _sync_order_with_erp(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync order with ERP system"""
        try:
            # This would integrate with your ERP system
            # For now, we'll simulate the sync
            
            sync_result = {
                'erp_order_id': f"ERP-{order_data['order_id']}",
                'sync_status': 'success',
                'sync_timestamp': datetime.now(timezone.utc).isoformat(),
                'fields_synced': ['order_id', 'supplier_id', 'delivery_date', 'items']
            }
            
            # TODO: Implement actual ERP sync
            logger.info(f"Would sync order {order_data['order_id']} with ERP")
            
            return sync_result
            
        except Exception as e:
            self.handle_error(e, "sync_order_with_erp")
            return {'error': str(e)}
    
    def _handle_order_delay(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Handle order delay and escalation"""
        try:
            order_id = data.get('order_id')
            delay_reason = data.get('delay_reason', 'Unknown')
            new_delivery_date = data.get('new_delivery_date')
            
            # Get current order context
            order_context = self.get_context(context_id)
            if not order_context:
                raise ValueError(f"No context found for order {order_id}")
            
            # Update order status
            order_context['status'] = 'delayed'
            order_context['delay_reason'] = delay_reason
            order_context['new_delivery_date'] = new_delivery_date
            order_context['delay_detected_at'] = datetime.now(timezone.utc).isoformat()
            
            # Determine escalation level
            escalation_level = self._determine_escalation_level(order_context)
            
            # Take escalation actions
            escalation_actions = self._execute_escalation_actions(order_id, escalation_level, order_context)
            
            # Update ERP with delay information
            erp_update = self._update_erp_with_delay(order_context)
            
            # Chat with supplier about delay
            if self.config['chat_enabled']:
                chat_response = self._chat_with_supplier_about_delay(order_context)
                order_context['supplier_chat'] = chat_response
            
            # Update context
            order_context['escalation_level'] = escalation_level
            order_context['escalation_actions'] = escalation_actions
            order_context['erp_update'] = erp_update
            
            self.update_context(context_id, order_context)
            
            result = {
                'order_id': order_id,
                'status': 'delayed',
                'escalation_level': escalation_level,
                'actions_taken': escalation_actions,
                'supplier_contacted': self.config['chat_enabled']
            }
            
            self.log_activity("Order delay handled", result)
            return result
            
        except Exception as e:
            self.handle_error(e, "handle_order_delay")
            return {'error': str(e)}
    
    def _determine_escalation_level(self, order_context: Dict[str, Any]) -> int:
        """Determine escalation level based on delay severity"""
        try:
            original_delivery = datetime.fromisoformat(order_context['delivery_date'].replace('Z', '+00:00'))
            new_delivery = datetime.fromisoformat(order_context.get('new_delivery_date', order_context['delivery_date']).replace('Z', '+00:00'))
            
            delay_days = (new_delivery - original_delivery).days
            
            if delay_days <= 1:
                return 1  # Low escalation
            elif delay_days <= 3:
                return 2  # Medium escalation
            else:
                return 3  # High escalation
                
        except Exception as e:
            self.handle_error(e, "determine_escalation_level")
            return 1
    
    def _execute_escalation_actions(self, order_id: str, escalation_level: int, 
                                   order_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute escalation actions based on level"""
        actions = []
        
        try:
            # Level 1: Internal notification
            if escalation_level >= 1:
                actions.append({
                    'action': 'internal_notification',
                    'recipients': ['procurement_team'],
                    'message': f"Order {order_id} delayed: {order_context.get('delay_reason')}",
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # Level 2: Supplier escalation
            if escalation_level >= 2:
                actions.append({
                    'action': 'supplier_escalation',
                    'supplier_id': order_context['supplier_id'],
                    'message': f"URGENT: Order {order_id} delay requires immediate attention",
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            # Level 3: Management escalation
            if escalation_level >= 3:
                actions.append({
                    'action': 'management_escalation',
                    'recipients': ['procurement_manager', 'operations_manager'],
                    'message': f"CRITICAL: Order {order_id} severely delayed - management intervention required",
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            
            return actions
            
        except Exception as e:
            self.handle_error(e, "execute_escalation_actions")
            return []
    
    def _update_erp_with_delay(self, order_context: Dict[str, Any]) -> Dict[str, Any]:
        """Update ERP system with delay information"""
        try:
            # This would update the ERP system with delay information
            erp_update = {
                'order_id': order_context['order_id'],
                'status': 'delayed',
                'delay_reason': order_context.get('delay_reason'),
                'new_delivery_date': order_context.get('new_delivery_date'),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # TODO: Implement actual ERP update
            logger.info(f"Would update ERP for order {order_context['order_id']}")
            
            return erp_update
            
        except Exception as e:
            self.handle_error(e, "update_erp_with_delay")
            return {'error': str(e)}
    
    def _chat_with_supplier_about_delay(self, order_context: Dict[str, Any]) -> Dict[str, Any]:
        """Chat with supplier about delay using AI"""
        try:
            ai_prompt = f"""
            Generate a professional message to supplier about order delay:
            
            Order ID: {order_context['order_id']}
            Original Delivery: {order_context['delivery_date']}
            New Delivery: {order_context.get('new_delivery_date')}
            Delay Reason: {order_context.get('delay_reason')}
            
            Be professional, understanding, but firm about the impact.
            Ask for:
            1. Confirmation of new delivery date
            2. Root cause analysis
            3. Prevention measures
            4. Regular updates
            """
            
            message = self.ai_client.generate_response(ai_prompt)
            
            return {
                'message': message,
                'sent_at': datetime.now(timezone.utc).isoformat(),
                'supplier_id': order_context['supplier_id']
            }
            
        except Exception as e:
            self.handle_error(e, "chat_with_supplier_about_delay")
            return {'error': str(e)}
    
    def _predict_delivery_delays(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict potential delivery delays using historical data"""
        try:
            # Use AI to analyze historical data and predict delays
            ai_prompt = f"""
            Analyze this order for potential delivery delays:
            
            Order: {order_data.get('order_id')}
            Supplier: {order_data.get('supplier_id')}
            Delivery Date: {order_data.get('delivery_date')}
            Items: {order_data.get('items', [])}
            
            Consider:
            - Supplier's historical performance
            - Item complexity
            - Lead time patterns
            - Seasonal factors
            - Current workload
            
            Provide:
            1. Delay probability (0-100%)
            2. Risk factors
            3. Mitigation recommendations
            4. Alternative suppliers if high risk
            """
            
            prediction = self.ai_client.generate_structured_response(ai_prompt)
            
            return {
                'order_id': order_data.get('order_id'),
                'prediction': prediction,
                'predicted_at': datetime.now(timezone.utc).isoformat(),
                'confidence': prediction.get('confidence', 0.5)
            }
            
        except Exception as e:
            self.handle_error(e, "predict_delivery_delays")
            return {'error': str(e)}
    
    def _handle_user_query(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Handle natural language queries about orders"""
        try:
            query = data.get('query', '')
            
            # Use AI to understand and respond to the query
            ai_prompt = f"""
            User query about orders: {query}
            
            Based on the current order context, provide a helpful response.
            Consider:
            - Order status and progress
            - Delivery tracking
            - Delay information
            - Supplier communications
            - Risk assessments
            
            Be specific and actionable.
            """
            
            response = self.ai_client.generate_response(ai_prompt)
            
            return {
                'query': query,
                'response': response,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.handle_error(e, "handle_user_query")
            return {'error': str(e)}
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of agent capabilities"""
        return self.capabilities
    
    def can_handle_event(self, event: AgentEvent) -> bool:
        """Check if agent can handle a specific event"""
        order_events = [
            AgentEvent.ORDER_CREATED,
            AgentEvent.ORDER_DELAYED,
            AgentEvent.USER_QUERY
        ]
        return event in order_events







