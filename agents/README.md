# ProcuraAI - Agentic Procurement System

## 🤖 Overview

ProcuraAI transforms your static procurement database into an intelligent, autonomous procurement co-pilot. The system consists of specialized AI agents that work together to automate procurement processes, provide insights, and handle complex queries through natural language.

## 🏗️ Architecture

### Core Components

1. **Agent Manager** - Orchestrates all agents and manages their lifecycle
2. **Context Manager** - Provides shared memory and coordination between agents
3. **Natural Language Interface** - ChatGPT-like interface for cross-module insights
4. **Specialized Agents** - Each handling specific procurement functions

### Agent Types

| Agent | Purpose | Capabilities |
|-------|---------|--------------|
| **RFQ Agent** | Autonomous Sourcing Assistant | Auto-source suppliers, generate RFQ content, parse quotes, build comparisons |
| **Order Agent** | Follow-Up & Delay Tracker | Monitor deliveries, escalate delays, sync with ERP, predict delays |
| **Supplier Agent** | Supplier Intelligence Analyst | Calculate performance scores, flag anomalies, suggest alternatives |
| **Contract Agent** | Contract Guardian | Monitor terms, track renewals, alert expirations, ensure compliance |

## 🚀 Quick Start

### 1. Access the AI Interface

Navigate to `/agents/chat` in your browser to access the ChatGPT-like interface.

### 2. Try Example Queries

- "Show me suppliers who quoted this month but didn't win any RFQs"
- "Find open POs with overdue delivery by more than 5 days"
- "Show me all expiring contracts in the next 30 days"
- "Which suppliers have the best performance ratings?"

### 3. Monitor System Status

Visit `/agents/dashboard` to see the status of all agents and system metrics.

## 📡 API Endpoints

### Core Endpoints

- `GET /agents/status` - Get overall system status
- `POST /agents/query` - Process natural language query
- `GET /agents/agents` - Get all agents status
- `GET /agents/agents/<agent_id>` - Get specific agent status

### Procurement Endpoints

- `POST /agents/rfq` - Create new RFQ
- `POST /agents/rfq/response` - Process quote response
- `POST /agents/order` - Create new order
- `POST /agents/order/delay` - Report order delay

### Interface Endpoints

- `GET /agents/chat` - AI chat interface
- `GET /agents/dashboard` - Agent dashboard
- `GET /agents/history` - Query history

## 🔧 Integration Examples

### Basic Integration

```python
from agents.flask_integration import (
    process_natural_language_query,
    trigger_rfq_created,
    trigger_order_created
)

# Process a natural language query
result = process_natural_language_query(
    "Show me underperforming suppliers",
    user_id="user123"
)

# Trigger RFQ creation
rfq_data = {
    'rfq_id': 'RFQ-001',
    'part_name': 'Bolt M8x20',
    'specifications': 'Stainless steel, ISO 4017',
    'quantity': 1000,
    'delivery_date': '2024-03-15'
}
success = trigger_rfq_created(rfq_data)
```

### Advanced Integration

```python
from agents.integration_example import (
    add_agentic_routes,
    integrate_with_existing_routes,
    add_ai_insights_to_dashboard
)

# Add agentic routes to your app
add_agentic_routes(app)

# Get integration functions
integration_functions = integrate_with_existing_routes()

# In your existing booking creation route
@app.route('/create_booking', methods=['POST'])
def create_booking():
    # ... existing logic ...
    
    # Notify AI agents
    integration_functions['on_booking_created'](booking_data)
    
    # ... rest of route ...
```

## 🎯 Agent Capabilities

### RFQ Agent
- **Auto-source suppliers** based on part category and performance
- **Generate RFQ content** from templates and specifications
- **Send RFQs** to suppliers via email/magic links
- **Parse responses** from Excel, PDF, email, or structured forms
- **Normalize data** and build comparison tables
- **Recommend suppliers** with reasoning

### Order Agent
- **Monitor confirmations** and delivery dates
- **Track delays** and escalate automatically
- **Sync with ERP** systems
- **Auto-update statuses** based on supplier communications
- **Chat with suppliers** about delays
- **Predict delays** using historical data

### Supplier Agent
- **Calculate performance scores** based on multiple metrics
- **Flag anomalies** in supplier behavior
- **Suggest alternatives** when suppliers underperform
- **Analyze trends** and patterns
- **Monitor quality** and competitiveness
- **Track price** fluctuations

### Contract Agent
- **Monitor terms** and conditions
- **Track renewal dates** and deadlines
- **Alert on expirations** and renewals
- **Propose renegotiation** triggers
- **Track consumption** and usage
- **Ensure compliance** with terms

## 🔍 Natural Language Queries

The system understands complex procurement queries in natural language:

### Supplier Performance
- "Show me suppliers who quoted this month but didn't win any RFQs"
- "Which suppliers have the best performance ratings?"
- "Find suppliers with quality issues in the last quarter"

### Order Tracking
- "Find open POs with overdue delivery by more than 5 days"
- "What orders are at risk of delay?"
- "Show me all orders from Supplier A"

### Contract Management
- "Show me all expiring contracts in the next 30 days"
- "Which contracts are underused?"
- "Find contracts with price escalation clauses"

### RFQ Analysis
- "Analyze recent RFQ responses and recommend the best supplier"
- "Show me the most competitive quotes this month"
- "Which RFQs need attention?"

## 📊 System Monitoring

### Agent Status
- **Running** - Agent is active and processing tasks
- **Busy** - Agent is currently handling a task
- **Idle** - Agent is waiting for tasks
- **Error** - Agent encountered an error

### Metrics
- Total agents
- Running agents
- Queued tasks
- Worker threads
- Active contexts

## 🛠️ Configuration

### Agent Configuration

```python
# In agents/core/constants.py
APP_NAME = "ProcuraAI"
PRIMARY_COLOR = "#0A2342"

# Agent capabilities
AGENT_CAPABILITIES = {
    'RFQ_AGENT': [
        'auto_source_suppliers',
        'generate_rfq_content',
        'send_rfq_emails',
        # ... more capabilities
    ]
}
```

### AI Configuration

```python
# In agents/utils/ai_client.py
AI_CONFIG = {
    'MODEL_NAME': 'gpt-4',
    'TEMPERATURE': 0.1,
    'MAX_TOKENS': 2000,
    'TIMEOUT': 30
}
```

## 🔧 Troubleshooting

### Common Issues

1. **Agents not starting**
   - Check system status at `/agents/status`
   - Verify all dependencies are installed
   - Check logs for error messages

2. **Natural language queries not working**
   - Ensure AI client is properly configured
   - Check if agents are running
   - Verify query format

3. **Integration issues**
   - Ensure Flask integration is properly initialized
   - Check route registration
   - Verify data format matches expected schema

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Future Enhancements

### Planned Features
- **Multi-language support** for international suppliers
- **Advanced analytics** with predictive modeling
- **Mobile app integration** for on-the-go access
- **Voice interface** for hands-free operation
- **Blockchain integration** for contract verification

### Custom Agents
- **Quality Agent** - Monitor quality metrics and standards
- **Compliance Agent** - Ensure regulatory compliance
- **Sustainability Agent** - Track environmental impact
- **Risk Agent** - Assess and mitigate procurement risks

## 📚 Additional Resources

- [Agent Architecture Guide](docs/agent-architecture.md)
- [API Reference](docs/api-reference.md)
- [Integration Examples](docs/integration-examples.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**ProcuraAI** - Transforming procurement with intelligent automation 🤖








