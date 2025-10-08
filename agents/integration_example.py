"""
Integration Example for ProcuraAI
Shows how to integrate the agentic system with existing Flask routes
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from agents.flask_integration import (
    process_natural_language_query,
    trigger_rfq_created,
    trigger_order_created,
    trigger_order_delay,
    get_agentic_system_status
)

def add_agentic_routes(app):
    """Add agentic routes to the existing Flask app"""
    
    @app.route('/ai-chat')
    @login_required
    def ai_chat():
        """AI Chat interface"""
        return render_template('agents/chat.html')
    
    @app.route('/ai-dashboard')
    @login_required
    def ai_dashboard():
        """AI Dashboard"""
        return render_template('agents/dashboard.html')
    
    @app.route('/ai-query', methods=['POST'])
    @login_required
    def ai_query():
        """Process AI query"""
        try:
            data = request.get_json()
            query = data.get('query', '')
            user_id = str(current_user.id)
            
            result = process_natural_language_query(query, user_id)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/ai-status')
    @login_required
    def ai_status():
        """Get AI system status"""
        try:
            status = get_agentic_system_status()
            return jsonify(status)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def integrate_with_existing_routes():
    """Example of how to integrate with existing routes"""
    
    # Example: When a user creates a booking (RFQ equivalent)
    def on_booking_created(booking_data):
        """Trigger when a booking is created"""
        try:
            # Convert booking data to RFQ format
            rfq_data = {
                'rfq_id': f"RFQ-{booking_data['id']}",
                'part_name': booking_data.get('service_name', 'Consultation'),
                'specifications': booking_data.get('description', ''),
                'quantity': 1,
                'delivery_date': booking_data.get('start_time', ''),
                'part_category': 'services'
            }
            
            # Trigger RFQ creation
            success = trigger_rfq_created(rfq_data)
            if success:
                print("✅ RFQ agent notified of new booking")
            else:
                print("⚠️  Failed to notify RFQ agent")
                
        except Exception as e:
            print(f"Error integrating booking creation: {e}")
    
    # Example: When a booking is confirmed (Order equivalent)
    def on_booking_confirmed(booking_data):
        """Trigger when a booking is confirmed"""
        try:
            # Convert booking data to order format
            order_data = {
                'order_id': f"ORD-{booking_data['id']}",
                'supplier_id': f"SUP-{booking_data['provider_id']}",
                'delivery_date': booking_data.get('start_time', ''),
                'items': [{
                    'name': booking_data.get('service_name', 'Consultation'),
                    'quantity': 1,
                    'price': booking_data.get('hourly_rate', 0)
                }]
            }
            
            # Trigger order creation
            success = trigger_order_created(order_data)
            if success:
                print("✅ Order agent notified of confirmed booking")
            else:
                print("⚠️  Failed to notify order agent")
                
        except Exception as e:
            print(f"Error integrating booking confirmation: {e}")
    
    # Example: When a booking is cancelled (Delay equivalent)
    def on_booking_cancelled(booking_data):
        """Trigger when a booking is cancelled"""
        try:
            # Convert booking data to delay format
            delay_data = {
                'order_id': f"ORD-{booking_data['id']}",
                'delay_reason': 'Booking cancelled by user',
                'new_delivery_date': None
            }
            
            # Trigger order delay
            success = trigger_order_delay(delay_data)
            if success:
                print("✅ Order agent notified of booking cancellation")
            else:
                print("⚠️  Failed to notify order agent")
                
        except Exception as e:
            print(f"Error integrating booking cancellation: {e}")
    
    return {
        'on_booking_created': on_booking_created,
        'on_booking_confirmed': on_booking_confirmed,
        'on_booking_cancelled': on_booking_cancelled
    }

def add_ai_insights_to_dashboard():
    """Example of adding AI insights to existing dashboard"""
    
    def get_ai_insights():
        """Get AI insights for the dashboard"""
        try:
            # Query the AI system for insights
            insights = []
            
            # Get supplier performance insights
            supplier_query = "Show me the top performing suppliers this month"
            supplier_result = process_natural_language_query(supplier_query)
            if supplier_result and not supplier_result.get('error'):
                insights.append({
                    'type': 'supplier_performance',
                    'title': 'Top Suppliers',
                    'content': supplier_result.get('response', ''),
                    'icon': '🏭'
                })
            
            # Get order tracking insights
            order_query = "What orders are at risk of delay?"
            order_result = process_natural_language_query(order_query)
            if order_result and not order_result.get('error'):
                insights.append({
                    'type': 'order_tracking',
                    'title': 'Order Alerts',
                    'content': order_result.get('response', ''),
                    'icon': '📦'
                })
            
            # Get contract insights
            contract_query = "Show me contracts expiring in the next 30 days"
            contract_result = process_natural_language_query(contract_query)
            if contract_result and not contract_result.get('error'):
                insights.append({
                    'type': 'contract_management',
                    'title': 'Expiring Contracts',
                    'content': contract_result.get('response', ''),
                    'icon': '📋'
                })
            
            return insights
            
        except Exception as e:
            print(f"Error getting AI insights: {e}")
            return []
    
    return get_ai_insights

# Example usage in your existing routes:
"""
# In your existing routes.py, you can add:

from agents.integration_example import (
    add_agentic_routes,
    integrate_with_existing_routes,
    add_ai_insights_to_dashboard
)

# Add the routes
add_agentic_routes(app)

# Get integration functions
integration_functions = integrate_with_existing_routes()
get_ai_insights = add_ai_insights_to_dashboard()

# In your existing booking creation route:
@app.route('/create_booking', methods=['POST'])
def create_booking():
    # ... existing booking creation logic ...
    
    # After successful booking creation:
    integration_functions['on_booking_created'](booking_data)
    
    # ... rest of your route ...

# In your existing dashboard route:
@app.route('/dashboard')
def dashboard():
    # ... existing dashboard logic ...
    
    # Add AI insights
    ai_insights = get_ai_insights()
    
    return render_template('dashboard.html', 
                         ai_insights=ai_insights,
                         # ... other variables ...)
"""








