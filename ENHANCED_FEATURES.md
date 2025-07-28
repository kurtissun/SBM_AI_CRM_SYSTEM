# Enhanced SBM AI CRM Features

## Overview
This document describes the new enhanced features added to the SBM AI CRM System for improved customer analytics and AI-powered campaign management.

## 1. Date/Time Filtering for Analytics

### Customer Insights Endpoint
The `/api/analytics/customer-insights` endpoint now supports date/time filtering:

**Parameters:**
- `start_date` (optional): ISO format datetime for start of analysis period
- `end_date` (optional): ISO format datetime for end of analysis period  
- `time_range` (optional): Predefined ranges - "7d", "30d", "90d", "1y", "custom"

**Example:**
```
GET /api/analytics/customer-insights?time_range=30d&segment_id=1
```

### Campaign Performance Analytics
The `/api/analytics/performance/campaigns` endpoint also supports the same date filtering parameters.

## 2. Enhanced AI Chatbot

### Features
The enhanced chatbot at `/api/chat/chat` provides:

1. **Deep Data Integration**
   - Real-time database queries
   - Actual customer and campaign metrics
   - Date range understanding from natural language

2. **Advanced Intent Recognition**
   - Campaign performance analysis
   - Customer churn prediction
   - CLV analysis
   - Business goal tracking
   - Predictive analytics

3. **SBM Goals Alignment**
   - Responses aligned with business goals
   - Performance tracking against KPIs
   - Strategic recommendations

### Example Queries
- "Show me campaign performance for last month"
- "Which customers are at risk of churning?"
- "How are we tracking against our revenue goals?"
- "What's the CLV of our premium segment?"
- "Predict next quarter's revenue"

### Response Format
```json
{
  "response": "AI-generated response",
  "intent": { "type": "campaign_analysis", "subtype": "performance" },
  "data_used": "Summary of data analyzed",
  "insights": [
    {
      "type": "optimization_opportunity",
      "title": "ROI Below Target",
      "description": "Average campaign ROI is below the 2x target",
      "recommendation": "Review targeting and messaging"
    }
  ],
  "suggested_actions": [
    {"action": "Optimize Underperformers", "urgency": "high", "impact": "immediate"}
  ],
  "visualizations": [
    {"type": "bar_chart", "title": "Campaign ROI Comparison", "data_key": "campaigns"}
  ],
  "sbm_alignment": {
    "aligned_goals": ["Revenue Growth"],
    "alignment_score": 0.8
  }
}
```

## 3. SBM Configuration Management

### Configuration API
New endpoints under `/api/sbm/` for managing business configuration:

**Endpoints:**
- `GET /api/sbm/config` - Get full configuration
- `GET /api/sbm/config/goals` - Get business goals
- `PUT /api/sbm/config/goals` - Update goals (admin only)
- `GET /api/sbm/config/focus-areas` - Get focus areas
- `PUT /api/sbm/config/focus-areas` - Update focus areas (admin only)
- `GET /api/sbm/config/ai-preferences` - Get AI preferences
- `PUT /api/sbm/config/ai-preferences` - Update AI preferences (admin only)
- `GET /api/sbm/config/performance` - Get goal performance metrics

### Default Goals
1. **Revenue Growth** - 20% annual increase
2. **Customer Satisfaction** - 90% satisfaction rating
3. **Market Expansion** - 15% market share in premium segment
4. **Digital Transformation** - Modernize customer touchpoints

### AI Preferences
Configure how the AI assistant behaves:
- Response style: professional_friendly, formal, casual, technical
- Risk tolerance: conservative, moderate, aggressive
- Innovation level: low, medium, high
- Data focus areas
- Cultural context

## 4. Integration Benefits

### For Admins
1. **Customizable Business Goals**
   - Set and track specific KPIs
   - Align AI responses with business strategy
   - Monitor progress in real-time

2. **Flexible Date Analysis**
   - Analyze any time period
   - Compare performance across periods
   - Identify trends and patterns

### For Users
1. **Natural Language Queries**
   - Ask questions in plain English
   - Get data-driven responses
   - Receive actionable recommendations

2. **Context-Aware Insights**
   - AI understands business goals
   - Recommendations align with strategy
   - Proactive alerts and suggestions

## Usage Examples

### 1. Analyzing Customer Segments by Date
```python
# API Call
GET /api/analytics/customer-insights?segment_id=1&time_range=90d

# Response includes date range context
{
  "customer_analysis": {
    "total_customers": 234,
    "date_range": {
      "start_date": "2024-09-01",
      "end_date": "2024-12-01",
      "days_analyzed": 90
    }
  }
}
```

### 2. Chatbot Campaign Analysis
```python
# Chat Request
POST /api/chat/chat
{
  "query": "How did our campaigns perform last month?"
}

# Enhanced Response
{
  "response": "Last month, you ran 5 campaigns with an average ROI of 2.3x...",
  "insights": [...],
  "suggested_actions": [...]
}
```

### 3. Updating Business Goals
```python
# Update Goals
PUT /api/sbm/config/goals
{
  "goals": [
    {
      "goal_id": "revenue_growth",
      "name": "Revenue Growth",
      "target_value": 25.0,
      "current_value": 15.0,
      ...
    }
  ]
}
```

## Security Considerations
- All configuration endpoints require authentication
- Goal/preference updates require admin permissions
- Chat history is stored securely per user
- Sensitive data is never exposed in AI responses

## Future Enhancements
1. Multi-language support for global operations
2. Voice-enabled chat interface
3. Automated goal adjustment based on market conditions
4. Integration with external data sources
5. Advanced predictive models with ML pipelines