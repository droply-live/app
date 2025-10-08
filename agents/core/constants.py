# Constants for the Agentic Core
# Centralized configuration for all agents and utilities

# App Configuration
APP_NAME = "ProcuraAI"
PRIMARY_COLOR = "#0A2342"
SECONDARY_COLOR = "#667eea"

# Agent Types
AGENT_TYPES = {
    'ACTION': 'action',
    'ANALYST': 'analyst', 
    'ADVISOR': 'advisor'
}

# Agent Capabilities
AGENT_CAPABILITIES = {
    'RFQ_AGENT': [
        'auto_source_suppliers',
        'generate_rfq_content',
        'send_rfq_emails',
        'parse_quote_responses',
        'normalize_quote_data',
        'build_comparison_tables',
        'recommend_suppliers'
    ],
    'ORDER_AGENT': [
        'monitor_confirmations',
        'track_delivery_dates',
        'escalate_delays',
        'sync_with_erp',
        'auto_update_statuses',
        'chat_with_suppliers',
        'predict_delays'
    ],
    'SUPPLIER_AGENT': [
        'calculate_performance_scores',
        'flag_anomalies',
        'suggest_alternatives',
        'analyze_trends',
        'monitor_quality',
        'track_competitiveness'
    ],
    'CONTRACT_AGENT': [
        'monitor_terms',
        'track_renewals',
        'alert_expirations',
        'propose_renegotiations',
        'track_consumption',
        'ensure_compliance'
    ]
}

# Natural Language Query Patterns
NL_QUERY_PATTERNS = {
    'SUPPLIER_PERFORMANCE': [
        'show me suppliers who quoted this month but didn\'t win',
        'find suppliers with poor performance',
        'which suppliers are underperforming'
    ],
    'ORDER_TRACKING': [
        'show me overdue orders',
        'find orders with delays',
        'which orders are late'
    ],
    'CONTRACT_MANAGEMENT': [
        'show me expiring contracts',
        'find contracts needing renewal',
        'which contracts are underused'
    ],
    'RFQ_ANALYSIS': [
        'show me recent RFQ responses',
        'find best quotes this month',
        'which RFQs need attention'
    ]
}

# Email Templates
EMAIL_TEMPLATES = {
    'RFQ_SEND': {
        'subject': 'RFQ Request - {part_name}',
        'body': '''
Dear {supplier_name},

We are requesting a quote for the following part:

Part: {part_name}
Specifications: {specifications}
Quantity: {quantity}
Delivery Required: {delivery_date}

Please respond by {response_deadline}.

Best regards,
{company_name}
        '''
    },
    'DELIVERY_REMINDER': {
        'subject': 'Delivery Reminder - Order {order_id}',
        'body': '''
Dear {supplier_name},

This is a reminder that order {order_id} is due for delivery on {delivery_date}.

Please confirm delivery status.

Best regards,
{company_name}
        '''
    }
}

# AI Model Configuration
AI_CONFIG = {
    'MODEL_NAME': 'gpt-4',
    'TEMPERATURE': 0.1,
    'MAX_TOKENS': 2000,
    'TIMEOUT': 30
}

# Database Table Mappings
TABLE_MAPPINGS = {
    'SUPPLIERS': 'supplier',
    'RFQS': 'rfq',
    'ORDERS': 'purchase_order',
    'CONTRACTS': 'contract',
    'PARTS': 'part'
}

# Status Enums
STATUS_ENUMS = {
    'RFQ_STATUS': ['draft', 'sent', 'responses_received', 'analyzed', 'awarded'],
    'ORDER_STATUS': ['pending', 'confirmed', 'in_production', 'shipped', 'delivered', 'delayed'],
    'SUPPLIER_STATUS': ['active', 'inactive', 'suspended', 'blacklisted'],
    'CONTRACT_STATUS': ['active', 'expired', 'terminated', 'pending_renewal']
}








