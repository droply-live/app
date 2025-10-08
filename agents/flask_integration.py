"""
Flask Integration for ProcuraAI
Integrates the agentic system with the existing Flask application
"""

from flask import Blueprint, request, jsonify, render_template
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timezone

from .procura_ai import ProcuraAI
from .core.constants import APP_NAME, PRIMARY_COLOR

logger = logging.getLogger(__name__)

# Create Blueprint for agentic routes
agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

# Global ProcuraAI instance
procura_ai = None

def init_agents(app):
    """Initialize the agentic system with the Flask app"""
    global procura_ai
    
    try:
        # Initialize ProcuraAI
        procura_ai = ProcuraAI()
        procura_ai.start()
        
        # Register the blueprint
        app.register_blueprint(agents_bp)
        
        logger.info(f"{APP_NAME} agentic system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize {APP_NAME} system: {e}")
        raise

@agents_bp.route('/status')
def get_system_status():
    """Get overall system status"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        status = procura_ai.get_system_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/query', methods=['POST'])
def process_query():
    """Process a natural language query"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        user_id = data.get('user_id')
        
        result = procura_ai.process_natural_language_query(query, user_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/rfq', methods=['POST'])
def create_rfq():
    """Create a new RFQ"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'RFQ data is required'}), 400
        
        result = procura_ai.create_rfq(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating RFQ: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/rfq/response', methods=['POST'])
def process_quote_response():
    """Process a quote response"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Response data is required'}), 400
        
        result = procura_ai.process_quote_response(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing quote response: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/order', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Order data is required'}), 400
        
        result = procura_ai.create_order(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/order/delay', methods=['POST'])
def report_order_delay():
    """Report an order delay"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Delay data is required'}), 400
        
        result = procura_ai.report_order_delay(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error reporting order delay: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/agents')
def get_agents():
    """Get all agents status"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        status = procura_ai.get_all_agent_status()
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting agents status: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/agents/<agent_id>')
def get_agent(agent_id):
    """Get specific agent status"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        status = procura_ai.get_agent_status(agent_id)
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/history')
def get_query_history():
    """Get query history"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 10))
        
        history = procura_ai.get_query_history(user_id, limit)
        return jsonify(history)
        
    except Exception as e:
        logger.error(f"Error getting query history: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/chat')
def chat_interface():
    """Render the chat interface"""
    try:
        return render_template('agents/chat.html', 
                             app_name=APP_NAME, 
                             primary_color=PRIMARY_COLOR)
        
    except Exception as e:
        logger.error(f"Error rendering chat interface: {e}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/dashboard')
def agent_dashboard():
    """Render the agent dashboard"""
    try:
        if not procura_ai:
            return jsonify({'error': 'System not initialized'}), 500
        
        system_status = procura_ai.get_system_status()
        return render_template('agents/dashboard.html', 
                             app_name=APP_NAME, 
                             primary_color=PRIMARY_COLOR,
                             system_status=system_status)
        
    except Exception as e:
        logger.error(f"Error rendering agent dashboard: {e}")
        return jsonify({'error': str(e)}), 500

# Utility functions for integration with existing routes
def trigger_rfq_created(rfq_data: Dict[str, Any]) -> bool:
    """Trigger RFQ created event"""
    try:
        if procura_ai:
            result = procura_ai.create_rfq(rfq_data)
            return result.get('status') == 'created'
        return False
    except Exception as e:
        logger.error(f"Error triggering RFQ created: {e}")
        return False

def trigger_order_created(order_data: Dict[str, Any]) -> bool:
    """Trigger order created event"""
    try:
        if procura_ai:
            result = procura_ai.create_order(order_data)
            return result.get('status') == 'created'
        return False
    except Exception as e:
        logger.error(f"Error triggering order created: {e}")
        return False

def trigger_order_delay(delay_data: Dict[str, Any]) -> bool:
    """Trigger order delay event"""
    try:
        if procura_ai:
            result = procura_ai.report_order_delay(delay_data)
            return result.get('status') == 'delay_reported'
        return False
    except Exception as e:
        logger.error(f"Error triggering order delay: {e}")
        return False

def process_natural_language_query(query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Process a natural language query"""
    try:
        if procura_ai:
            return procura_ai.process_natural_language_query(query, user_id)
        return {'error': 'System not initialized'}
    except Exception as e:
        logger.error(f"Error processing natural language query: {e}")
        return {'error': str(e)}

def get_agentic_system_status() -> Dict[str, Any]:
    """Get agentic system status"""
    try:
        if procura_ai:
            return procura_ai.get_system_status()
        return {'error': 'System not initialized'}
    except Exception as e:
        logger.error(f"Error getting agentic system status: {e}")
        return {'error': str(e)}








