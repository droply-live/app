"""
RFQ Agent - Autonomous Sourcing Assistant
Handles RFQ creation, supplier sourcing, quote analysis, and recommendations
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
import json
import logging

from .base_agent import BaseAgent, AgentCapability
from ..core.agent_manager import AgentEvent
from ..core.context_manager import ContextType
from ..utils.ai_client import AIClient
from ..utils.email_parser import EmailParser
from ..utils.pdf_parser import PDFParser
from ..core.constants import EMAIL_TEMPLATES, STATUS_ENUMS

logger = logging.getLogger(__name__)

class RFQAgent(BaseAgent):
    """
    RFQ Agent - Autonomous Sourcing Assistant
    
    Capabilities:
    - Auto-source suppliers based on part category and performance
    - Generate RFQ content from templates and part specs
    - Send RFQs to suppliers via email/magic links
    - Parse and normalize quote responses
    - Build comparison tables and recommendations
    """
    
    def __init__(self, agent_id: str = "rfq_agent"):
        capabilities = [
            AgentCapability.AUTO_SOURCE,
            AgentCapability.GENERATE_CONTENT,
            AgentCapability.SEND_EMAILS,
            AgentCapability.PARSE_RESPONSES,
            AgentCapability.NORMALIZE_DATA,
            AgentCapability.BUILD_COMPARISONS,
            AgentCapability.RECOMMEND
        ]
        
        super().__init__(agent_id, "RFQ", capabilities)
        self.email_parser = EmailParser()
        self.pdf_parser = PDFParser()
        
        # RFQ-specific configuration
        self.config.update({
            'max_suppliers_per_rfq': 10,
            'response_deadline_hours': 72,
            'auto_send_enabled': True,
            'template_language': 'en'
        })
    
    def handle_event(self, event: AgentEvent, data: Dict[str, Any], context_id: str) -> Any:
        """Handle RFQ-related events"""
        try:
            self.log_activity(f"Handling event: {event.value}", data)
            
            if event == AgentEvent.RFQ_CREATED:
                return self._process_new_rfq(data, context_id)
            elif event == AgentEvent.RFQ_RESPONSE_RECEIVED:
                return self._process_quote_response(data, context_id)
            elif event == AgentEvent.USER_QUERY:
                return self._handle_user_query(data, context_id)
            else:
                logger.warning(f"Unhandled event type: {event}")
                return None
                
        except Exception as e:
            self.handle_error(e, f"handle_event for {event.value}")
            return None
    
    def _process_new_rfq(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Process a new RFQ request"""
        try:
            # Validate required fields
            required_fields = ['part_name', 'specifications', 'quantity', 'delivery_date']
            if not self.validate_data(data, required_fields):
                raise ValueError("Missing required RFQ fields")
            
            # Auto-source suppliers
            suppliers = self._auto_source_suppliers(data)
            
            # Generate RFQ content
            rfq_content = self._generate_rfq_content(data)
            
            # Send RFQs to suppliers
            sent_count = self._send_rfqs_to_suppliers(suppliers, rfq_content, data)
            
            # Update context
            result = {
                'rfq_id': data.get('rfq_id'),
                'suppliers_contacted': sent_count,
                'total_suppliers': len(suppliers),
                'rfq_content': rfq_content,
                'status': 'sent'
            }
            
            self.update_context(context_id, result)
            self.log_activity("RFQ processed and sent", result)
            
            return result
            
        except Exception as e:
            self.handle_error(e, "process_new_rfq")
            return {'error': str(e)}
    
    def _auto_source_suppliers(self, rfq_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Auto-source suppliers based on part category and performance"""
        try:
            part_category = rfq_data.get('part_category', 'general')
            part_name = rfq_data.get('part_name', '')
            
            # Use AI to find relevant suppliers
            ai_prompt = f"""
            Find the best suppliers for this RFQ:
            Part: {part_name}
            Category: {part_category}
            Specifications: {rfq_data.get('specifications', '')}
            
            Consider:
            - Supplier performance history
            - Part category expertise
            - Geographic proximity
            - Previous quote success rate
            - Quality ratings
            
            Return top {self.config['max_suppliers_per_rfq']} suppliers with contact info.
            """
            
            ai_response = self.ai_client.generate_response(ai_prompt)
            
            # Parse AI response to extract supplier data
            suppliers = self._parse_supplier_recommendations(ai_response)
            
            self.log_activity("Auto-sourced suppliers", {'count': len(suppliers)})
            return suppliers
            
        except Exception as e:
            self.handle_error(e, "auto_source_suppliers")
            return []
    
    def _generate_rfq_content(self, rfq_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate RFQ content using templates and AI"""
        try:
            template = EMAIL_TEMPLATES['RFQ_SEND']
            
            # Use AI to customize the template
            ai_prompt = f"""
            Customize this RFQ email template for:
            Part: {rfq_data.get('part_name')}
            Specifications: {rfq_data.get('specifications')}
            Quantity: {rfq_data.get('quantity')}
            Delivery: {rfq_data.get('delivery_date')}
            
            Make it professional and specific to the part requirements.
            """
            
            customized_content = self.ai_client.generate_response(ai_prompt)
            
            # Fill template variables
            content = {
                'subject': template['subject'].format(
                    part_name=rfq_data.get('part_name', 'Unknown Part')
                ),
                'body': customized_content,
                'response_deadline': (datetime.now() + timedelta(hours=self.config['response_deadline_hours'])).isoformat()
            }
            
            return content
            
        except Exception as e:
            self.handle_error(e, "generate_rfq_content")
            return {'error': str(e)}
    
    def _send_rfqs_to_suppliers(self, suppliers: List[Dict[str, Any]], 
                               rfq_content: Dict[str, str], rfq_data: Dict[str, Any]) -> int:
        """Send RFQs to suppliers via email"""
        sent_count = 0
        
        try:
            for supplier in suppliers:
                if self._send_rfq_email(supplier, rfq_content, rfq_data):
                    sent_count += 1
                    
            self.log_activity("RFQs sent to suppliers", {'sent_count': sent_count})
            return sent_count
            
        except Exception as e:
            self.handle_error(e, "send_rfqs_to_suppliers")
            return sent_count
    
    def _send_rfq_email(self, supplier: Dict[str, Any], rfq_content: Dict[str, str], 
                        rfq_data: Dict[str, Any]) -> bool:
        """Send RFQ email to a single supplier"""
        try:
            # This would integrate with your email service
            # For now, we'll simulate the email sending
            
            email_data = {
                'to': supplier.get('email'),
                'subject': rfq_content['subject'],
                'body': rfq_content['body'],
                'supplier_name': supplier.get('name'),
                'rfq_id': rfq_data.get('rfq_id')
            }
            
            # TODO: Integrate with actual email service (SendGrid, AWS SES, etc.)
            logger.info(f"Would send RFQ email to {supplier.get('email')}")
            
            return True
            
        except Exception as e:
            self.handle_error(e, f"send_rfq_email to {supplier.get('email')}")
            return False
    
    def _process_quote_response(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Process incoming quote responses"""
        try:
            response_data = data.get('response_data', {})
            response_type = data.get('response_type', 'email')  # email, pdf, excel, structured
            
            # Parse response based on type
            if response_type == 'email':
                parsed_data = self.email_parser.parse_quote_response(response_data)
            elif response_type == 'pdf':
                parsed_data = self.pdf_parser.parse_quote_response(response_data)
            else:
                parsed_data = response_data
            
            # Normalize the data
            normalized_quote = self._normalize_quote_data(parsed_data)
            
            # Update context with new quote
            current_context = self.get_context(context_id)
            if current_context:
                quotes = current_context.get('quotes', [])
                quotes.append(normalized_quote)
                current_context['quotes'] = quotes
                self.update_context(context_id, current_context)
            
            # Generate comparison if we have multiple quotes
            if len(current_context.get('quotes', [])) > 1:
                comparison = self._build_comparison_table(current_context.get('quotes', []))
                self.update_context(context_id, {'comparison': comparison})
            
            result = {
                'quote_id': normalized_quote.get('quote_id'),
                'supplier': normalized_quote.get('supplier_name'),
                'price': normalized_quote.get('price'),
                'delivery': normalized_quote.get('delivery_date'),
                'status': 'processed'
            }
            
            self.log_activity("Quote response processed", result)
            return result
            
        except Exception as e:
            self.handle_error(e, "process_quote_response")
            return {'error': str(e)}
    
    def _normalize_quote_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize quote data from various sources"""
        try:
            # Use AI to extract and normalize key information
            ai_prompt = f"""
            Extract and normalize this quote data:
            {json.dumps(raw_data, indent=2)}
            
            Return structured data with:
            - supplier_name
            - price (numeric)
            - currency
            - delivery_date
            - payment_terms
            - quote_validity
            - part_number
            - specifications
            """
            
            normalized = self.ai_client.generate_structured_response(ai_prompt)
            
            # Add metadata
            normalized.update({
                'quote_id': f"quote_{datetime.now().timestamp()}",
                'received_at': datetime.now(timezone.utc).isoformat(),
                'status': 'pending_review'
            })
            
            return normalized
            
        except Exception as e:
            self.handle_error(e, "normalize_quote_data")
            return raw_data
    
    def _build_comparison_table(self, quotes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build comparison table and recommendations"""
        try:
            if len(quotes) < 2:
                return {'message': 'Need at least 2 quotes for comparison'}
            
            # Use AI to analyze and compare quotes
            ai_prompt = f"""
            Analyze and compare these quotes:
            {json.dumps(quotes, indent=2)}
            
            Provide:
            1. Price comparison (best, worst, average)
            2. Delivery comparison
            3. Overall recommendation with reasoning
            4. Risk assessment
            5. Cost-benefit analysis
            """
            
            analysis = self.ai_client.generate_structured_response(ai_prompt)
            
            # Add summary metrics
            prices = [float(q.get('price', 0)) for q in quotes if q.get('price')]
            if prices:
                analysis['price_summary'] = {
                    'lowest': min(prices),
                    'highest': max(prices),
                    'average': sum(prices) / len(prices),
                    'savings_potential': max(prices) - min(prices)
                }
            
            return analysis
            
        except Exception as e:
            self.handle_error(e, "build_comparison_table")
            return {'error': str(e)}
    
    def _parse_supplier_recommendations(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response to extract supplier recommendations"""
        try:
            # This would parse the AI response to extract structured supplier data
            # For now, return mock data
            return [
                {
                    'name': 'Supplier A',
                    'email': 'contact@supplier-a.com',
                    'expertise': 'Electronics',
                    'rating': 4.5,
                    'response_time': '24h'
                },
                {
                    'name': 'Supplier B', 
                    'email': 'quotes@supplier-b.com',
                    'expertise': 'Mechanical',
                    'rating': 4.2,
                    'response_time': '48h'
                }
            ]
        except Exception as e:
            self.handle_error(e, "parse_supplier_recommendations")
            return []
    
    def _handle_user_query(self, data: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """Handle natural language queries about RFQs"""
        try:
            query = data.get('query', '')
            
            # Use AI to understand and respond to the query
            ai_prompt = f"""
            User query about RFQs: {query}
            
            Based on the current RFQ context, provide a helpful response.
            Consider:
            - Current RFQ status
            - Quote comparisons
            - Supplier performance
            - Recommendations
            
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
        rfq_events = [
            AgentEvent.RFQ_CREATED,
            AgentEvent.RFQ_RESPONSE_RECEIVED,
            AgentEvent.USER_QUERY
        ]
        return event in rfq_events







