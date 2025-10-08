"""
Contract Agent - Contract Guardian
Monitors contracts, tracks renewals, and ensures compliance
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
import json
import logging

from .base_agent import BaseAgent, AgentCapability
from ..core.agent_manager import AgentEvent
from ..core.context_manager import ContextType
from ..utils.ai_client import AIClient

logger = logging.getLogger(__name__)

class ContractAgent(BaseAgent):
    """
    Contract Agent - Contract Guardian
    
    Capabilities:
    - Monitor contract terms and conditions
    - Track renewal dates and deadlines
    - Alert on expirations and renewals
    - Propose renegotiation triggers
    - Track consumption and usage
    - Ensure compliance with terms
    """
    
    def __init__(self, agent_id: str = "contract_agent"):
        capabilities = [
            AgentCapability.MONITOR,
            AgentCapability.TRACK,
            AgentCapability.ALERT,
            AgentCapability.PROPOSE,
            AgentCapability.ENSURE,
            AgentCapability.ANALYZE
        ]
        
        super().__init__(agent_id, "Contract", capabilities)
        
        # Contract-specific configuration
        self.config.update({
            'renewal_alert_days': 90,  # Alert 90 days before expiry
            'compliance_check_interval': 7,  # Check compliance weekly
            'consumption_tracking_enabled': True,
            'auto_renewal_threshold': 0.8,  # Auto-renew if 80% of contract value used
            'renegotiation_threshold': 0.9  # Suggest renegotiation at 90% usage
        })
    
    def handle_event(self, event: AgentEvent, data: Dict[str, Any], context_id: str) -> Any:
        """Handle contract-related events"""
        try:
            self.log_activity(f"Handling event: {event.value}", data)
            
            if event == AgentEvent.CONTRACT_EXPIRING:
                return self._process_contract_expiry(data, context_id)
            elif event == AgentEvent.USER_QUERY:
                return self._handle_user_query(data, context_id)
            else:
                logger.warning(f"Unhandled event type: {event}")
                return None
                
        except Exception as e:
            self.handle_error(e, f"handle_event for {event.value}")
            return None
    
    def _process_contract_expiry(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Process contract expiry and generate actions"""
        try:
            contract_id = data.get('contract_id')
            if not contract_id:
                raise ValueError("Missing contract_id")
            
            # Get contract details
            contract_data = self._get_contract_data(contract_id)
            
            # Check expiry status
            expiry_status = self._check_expiry_status(contract_data)
            
            # Generate renewal recommendations
            renewal_recommendations = self._generate_renewal_recommendations(contract_data, expiry_status)
            
            # Check compliance
            compliance_status = self._check_compliance(contract_data)
            
            # Track consumption
            consumption_data = self._track_consumption(contract_data)
            
            # Generate actions
            actions = self._generate_actions(contract_data, expiry_status, compliance_status, consumption_data)
            
            # Update context
            result = {
                'contract_id': contract_id,
                'expiry_status': expiry_status,
                'renewal_recommendations': renewal_recommendations,
                'compliance_status': compliance_status,
                'consumption_data': consumption_data,
                'actions': actions,
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
            
            self.update_context(context_id, result)
            self.log_activity("Contract expiry processed", result)
            
            return result
            
        except Exception as e:
            self.handle_error(e, "process_contract_expiry")
            return {'error': str(e)}
    
    def _get_contract_data(self, contract_id: str) -> Dict[str, Any]:
        """Get contract data from database"""
        try:
            # This would query the database for contract data
            # For now, return mock data
            contract_data = {
                'contract_id': contract_id,
                'supplier_id': 'SUP-001',
                'supplier_name': 'Supplier A',
                'start_date': '2023-01-01',
                'end_date': '2024-12-31',
                'total_value': 100000.00,
                'used_value': 75000.00,
                'terms': {
                    'payment_terms': 'Net 30',
                    'delivery_terms': 'FOB Destination',
                    'quality_standards': 'ISO 9001',
                    'warranty_period': '12 months'
                },
                'renewal_options': {
                    'auto_renewal': True,
                    'renewal_period': '12 months',
                    'price_escalation': '3% annually'
                },
                'compliance_requirements': [
                    'Monthly performance reports',
                    'Quality certifications',
                    'Insurance coverage',
                    'Environmental compliance'
                ]
            }
            
            return contract_data
            
        except Exception as e:
            self.handle_error(e, "get_contract_data")
            return {}
    
    def _check_expiry_status(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check contract expiry status"""
        try:
            end_date = datetime.fromisoformat(contract_data['end_date'])
            current_date = datetime.now(timezone.utc)
            
            days_until_expiry = (end_date - current_date).days
            
            if days_until_expiry < 0:
                status = 'expired'
            elif days_until_expiry <= 30:
                status = 'expiring_soon'
            elif days_until_expiry <= 90:
                status = 'expiring_soon'
            else:
                status = 'active'
            
            return {
                'status': status,
                'days_until_expiry': days_until_expiry,
                'expiry_date': contract_data['end_date'],
                'requires_action': status in ['expired', 'expiring_soon']
            }
            
        except Exception as e:
            self.handle_error(e, "check_expiry_status")
            return {'status': 'unknown', 'days_until_expiry': 0, 'requires_action': False}
    
    def _generate_renewal_recommendations(self, contract_data: Dict[str, Any], 
                                        expiry_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate renewal recommendations"""
        recommendations = []
        
        try:
            if not expiry_status.get('requires_action', False):
                return recommendations
            
            # Check if contract has auto-renewal
            renewal_options = contract_data.get('renewal_options', {})
            auto_renewal = renewal_options.get('auto_renewal', False)
            
            if auto_renewal:
                recommendations.append({
                    'type': 'auto_renewal',
                    'priority': 'medium',
                    'description': 'Contract has auto-renewal enabled',
                    'action': 'Verify auto-renewal terms and conditions',
                    'timeline': '30 days'
                })
            else:
                recommendations.append({
                    'type': 'manual_renewal',
                    'priority': 'high',
                    'description': 'Contract requires manual renewal',
                    'action': 'Initiate renewal process with supplier',
                    'timeline': '60 days'
                })
            
            # Check consumption for renewal decision
            total_value = contract_data.get('total_value', 0)
            used_value = contract_data.get('used_value', 0)
            usage_percentage = (used_value / total_value) * 100 if total_value > 0 else 0
            
            if usage_percentage > 80:
                recommendations.append({
                    'type': 'high_usage_renewal',
                    'priority': 'high',
                    'description': f'Contract usage is {usage_percentage:.1f}% - consider renewal',
                    'action': 'Evaluate renewal terms and pricing',
                    'timeline': '45 days'
                })
            
            # Check for price escalation
            price_escalation = renewal_options.get('price_escalation', '0%')
            if price_escalation != '0%':
                recommendations.append({
                    'type': 'price_escalation',
                    'priority': 'medium',
                    'description': f'Contract has {price_escalation} price escalation',
                    'action': 'Review price escalation impact on budget',
                    'timeline': '30 days'
                })
            
            return recommendations
            
        except Exception as e:
            self.handle_error(e, "generate_renewal_recommendations")
            return []
    
    def _check_compliance(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check contract compliance"""
        try:
            compliance_requirements = contract_data.get('compliance_requirements', [])
            compliance_status = {
                'overall_compliance': 'compliant',
                'requirements': [],
                'violations': [],
                'last_check': datetime.now(timezone.utc).isoformat()
            }
            
            # Check each compliance requirement
            for requirement in compliance_requirements:
                # This would check actual compliance status
                # For now, simulate compliance check
                is_compliant = True  # Mock compliance check
                
                compliance_status['requirements'].append({
                    'requirement': requirement,
                    'status': 'compliant' if is_compliant else 'non_compliant',
                    'last_verified': datetime.now(timezone.utc).isoformat()
                })
                
                if not is_compliant:
                    compliance_status['violations'].append({
                        'requirement': requirement,
                        'severity': 'medium',
                        'description': f'Non-compliance with {requirement}',
                        'action_required': 'Address compliance issue'
                    })
            
            # Update overall compliance status
            if compliance_status['violations']:
                compliance_status['overall_compliance'] = 'non_compliant'
            
            return compliance_status
            
        except Exception as e:
            self.handle_error(e, "check_compliance")
            return {'overall_compliance': 'unknown', 'requirements': [], 'violations': []}
    
    def _track_consumption(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track contract consumption and usage"""
        try:
            total_value = contract_data.get('total_value', 0)
            used_value = contract_data.get('used_value', 0)
            usage_percentage = (used_value / total_value) * 100 if total_value > 0 else 0
            
            # Calculate consumption rate
            start_date = datetime.fromisoformat(contract_data['start_date'])
            current_date = datetime.now(timezone.utc)
            days_elapsed = (current_date - start_date).days
            total_days = 365  # Assume 1-year contract
            
            expected_usage = (days_elapsed / total_days) * 100
            usage_variance = usage_percentage - expected_usage
            
            consumption_data = {
                'total_value': total_value,
                'used_value': used_value,
                'remaining_value': total_value - used_value,
                'usage_percentage': round(usage_percentage, 2),
                'expected_usage': round(expected_usage, 2),
                'usage_variance': round(usage_variance, 2),
                'consumption_rate': round(usage_percentage / (days_elapsed / 30), 2),  # Monthly rate
                'projected_completion': self._project_completion_date(usage_percentage, days_elapsed, total_days)
            }
            
            return consumption_data
            
        except Exception as e:
            self.handle_error(e, "track_consumption")
            return {'error': str(e)}
    
    def _project_completion_date(self, usage_percentage: float, days_elapsed: int, total_days: int) -> str:
        """Project contract completion date based on usage"""
        try:
            if usage_percentage <= 0:
                return 'unknown'
            
            # Calculate remaining days based on current usage rate
            remaining_percentage = 100 - usage_percentage
            days_remaining = (remaining_percentage / usage_percentage) * days_elapsed
            
            projected_date = datetime.now(timezone.utc) + timedelta(days=int(days_remaining))
            return projected_date.isoformat()
            
        except Exception as e:
            self.handle_error(e, "project_completion_date")
            return 'unknown'
    
    def _generate_actions(self, contract_data: Dict[str, Any], expiry_status: Dict[str, Any],
                         compliance_status: Dict[str, Any], consumption_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actions based on contract analysis"""
        actions = []
        
        try:
            # Expiry actions
            if expiry_status.get('requires_action', False):
                if expiry_status['status'] == 'expired':
                    actions.append({
                        'type': 'expired_contract',
                        'priority': 'critical',
                        'description': 'Contract has expired',
                        'action': 'Immediately renew or terminate contract',
                        'timeline': '1 day'
                    })
                elif expiry_status['status'] == 'expiring_soon':
                    actions.append({
                        'type': 'expiring_contract',
                        'priority': 'high',
                        'description': f"Contract expires in {expiry_status['days_until_expiry']} days",
                        'action': 'Initiate renewal process',
                        'timeline': '30 days'
                    })
            
            # Compliance actions
            if compliance_status.get('overall_compliance') == 'non_compliant':
                for violation in compliance_status.get('violations', []):
                    actions.append({
                        'type': 'compliance_violation',
                        'priority': 'high',
                        'description': violation['description'],
                        'action': violation['action_required'],
                        'timeline': '7 days'
                    })
            
            # Consumption actions
            usage_percentage = consumption_data.get('usage_percentage', 0)
            if usage_percentage > 90:
                actions.append({
                    'type': 'high_consumption',
                    'priority': 'medium',
                    'description': f'Contract usage is {usage_percentage:.1f}% - approaching limit',
                    'action': 'Monitor usage closely and prepare for renewal',
                    'timeline': '30 days'
                })
            elif usage_percentage > 80:
                actions.append({
                    'type': 'moderate_consumption',
                    'priority': 'low',
                    'description': f'Contract usage is {usage_percentage:.1f}% - monitor usage',
                    'action': 'Track usage patterns and plan accordingly',
                    'timeline': '60 days'
                })
            
            # Renegotiation actions
            if usage_percentage > 95:
                actions.append({
                    'type': 'renegotiation_trigger',
                    'priority': 'medium',
                    'description': 'Contract usage threshold exceeded',
                    'action': 'Consider renegotiating terms or expanding contract',
                    'timeline': '45 days'
                })
            
            return actions
            
        except Exception as e:
            self.handle_error(e, "generate_actions")
            return []
    
    def _handle_user_query(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Handle natural language queries about contracts"""
        try:
            query = data.get('query', '')
            
            # Use AI to understand and respond to the query
            ai_prompt = f"""
            User query about contracts: {query}
            
            Based on the current contract context, provide a helpful response.
            Consider:
            - Contract expiry dates
            - Renewal requirements
            - Compliance status
            - Consumption tracking
            - Renegotiation opportunities
            
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
        contract_events = [
            AgentEvent.CONTRACT_EXPIRING,
            AgentEvent.USER_QUERY
        ]
        return event in contract_events








