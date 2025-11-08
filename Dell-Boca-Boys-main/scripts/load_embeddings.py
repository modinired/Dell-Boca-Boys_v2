#!/usr/bin/env python3
"""
Load n8n super user manual into knowledge base.
Initializes the system with foundational n8n knowledge.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.tools.memory import memory
from app.utils.logging import logger


N8N_MANUAL = """
# n8n Super User Manual - Expert Knowledge Base

## Core Concepts

### Workflows
A workflow is a collection of nodes connected together to automate tasks. Each workflow:
- Has a unique name and ID
- Can be active or inactive
- Starts with a trigger node
- Processes data through connected nodes
- Can include error handling and branching logic

### Nodes
Nodes are the building blocks of workflows:
- **Trigger Nodes**: Start the workflow (Webhook, Schedule, Manual, Error Trigger)
- **Regular Nodes**: Process data (HTTP Request, Set, Function, Code)
- **Logic Nodes**: Control flow (IF, Switch, Merge, Split in Batches)

### Connections
Connections define data flow between nodes:
- Main connection: Primary data path
- Multiple outputs: From IF, Switch nodes
- Error connections: For error handling

## Best Practices

### Error Handling
1. **Use Error Trigger Workflow**: Create separate workflow for error handling
2. **Add Error Workflow**: Connect Error Trigger to main workflow
3. **Implement Retries**: Configure retry logic on HTTP nodes
4. **Validate Data**: Use IF nodes to check data before processing

### HTTP Request Best Practices
```
Required Settings:
- Method: GET/POST/PUT/DELETE as appropriate
- URL: Full URL with protocol
- Authentication: Use credential aliases
- Options:
  - Retry on Fail: Enabled
  - Max Retries: 3
  - Retry Backoff: exponential
  - Timeout: 30-60 seconds
```

### Credential Management
- NEVER embed raw credentials in workflows
- ALWAYS use credential aliases
- Create credentials in n8n UI first
- Reference by name in nodes

### Loop Safety
When using Split in Batches:
- Always set explicit batchSize (default: 10)
- Implement completion check
- Add timeout protection
- Test with small datasets first

### Data Transformation
1. **Set Node**: Simple field mapping and transformations
2. **Code Node**: Complex logic using JavaScript
3. **Function Node**: Item-level transformations
4. **Aggregate Node**: Combining data

## Common Patterns

### Webhook to Database Pattern
```
Webhook (Trigger)
→ Validate Input (IF Node)
  → Valid: Transform Data (Set)
    → Save to Database (Postgres/MySQL)
    → Return Success (Respond to Webhook)
  → Invalid: Return Error (Respond to Webhook)
```

### API Integration Pattern
```
Schedule Trigger (Every 5 minutes)
→ Fetch Data (HTTP Request with Retry)
→ Check for New Items (IF Node)
  → Process Items (Split in Batches)
    → Transform (Set)
    → Send to API (HTTP Request)
```

### Error Recovery Pattern
```
Main Workflow:
  [Trigger] → [Process] → [Success]
         ↓ (on error)
  Error Workflow (Error Trigger):
    → Log Error → Notify Admin → Retry Logic
```

## Performance Tips

1. **Minimize Node Count**: Combine operations where possible
2. **Use Pagination**: For large datasets
3. **Implement Caching**: Store frequently accessed data
4. **Optimize Queries**: Use filters to reduce data volume
5. **Batch Operations**: Process multiple items together

## Security Guidelines

1. **Credentials**: Only use aliases, never raw values
2. **Input Validation**: Always validate webhook/external inputs
3. **Output Sanitization**: Clean data before external sends
4. **Access Control**: Limit workflow permissions
5. **Audit Logging**: Enable for production workflows

## Node Parameter Patterns

### HTTP Request Node
```json
{
  "url": "https://api.example.com/data",
  "method": "GET",
  "authentication": "genericCredentialType",
  "options": {
    "retry": {
      "maxRetries": 3,
      "retryBackoff": "exponential"
    },
    "timeout": 30000
  }
}
```

### IF Node
```json
{
  "conditions": {
    "boolean": [],
    "number": [
      {
        "value1": "={{$json.status_code}}",
        "operation": "equal",
        "value2": 200
      }
    ]
  }
}
```

### Set Node
```json
{
  "values": {
    "string": [
      {
        "name": "output_field",
        "value": "={{$json.input_field}}"
      }
    ]
  },
  "options": {}
}
```

### Split in Batches
```json
{
  "batchSize": 10,
  "options": {
    "reset": false
  }
}
```

## Workflow Structure Guidelines

1. **Start with Trigger**: Every workflow needs exactly one trigger
2. **Linear Flow**: Keep flow simple and predictable
3. **Branch Carefully**: Use IF/Switch for conditional logic
4. **Merge Paths**: Use Merge node to combine branches
5. **End Cleanly**: Ensure all paths complete

## Testing Workflows

1. **Start Inactive**: Always create workflows inactive
2. **Test with Manual Trigger**: Use Manual Trigger for initial testing
3. **Validate Output**: Check each node's output
4. **Test Error Cases**: Trigger errors intentionally
5. **Monitor Executions**: Check execution history

## Production Checklist

Before activating:
- [ ] Error handling implemented
- [ ] Credentials use aliases only
- [ ] Retries configured on HTTP nodes
- [ ] Input validation in place
- [ ] Loops have termination conditions
- [ ] Tested with realistic data
- [ ] Monitoring/alerting configured
- [ ] Documentation updated

## Common Nodes Reference

### Triggers
- **Webhook**: HTTP endpoint for external calls
- **Schedule**: Time-based triggers (cron)
- **Manual**: For testing and manual runs
- **Error Trigger**: Catches errors from other workflows

### Data Processing
- **Set**: Set/update fields
- **Code**: JavaScript code execution
- **Function**: Per-item JavaScript
- **Aggregate**: Combine multiple items

### Logic
- **IF**: Binary conditional
- **Switch**: Multiple conditional branches
- **Merge**: Combine data from multiple sources
- **Split in Batches**: Process items in batches

### External Services
- **HTTP Request**: API calls
- **Webhook**: Receive HTTP requests
- **Postgres/MySQL**: Database operations
- **Redis**: Cache operations

## Expressions

n8n uses expressions for dynamic values:
- `{{$json.field}}`: Access current item data
- `={{$node["NodeName"].json.field}}`: Access other node's data
- `={{$now}}`: Current timestamp
- `={{$json.field.toLowerCase()}}`: JavaScript methods

## Common Issues & Solutions

### Issue: Infinite Loop
**Solution**: Add explicit batchSize to Split in Batches

### Issue: Workflow Not Triggering
**Solution**: Check that workflow is active and trigger is configured

### Issue: Credentials Not Found
**Solution**: Verify credential exists and name matches exactly

### Issue: Timeout Errors
**Solution**: Increase timeout in node options or implement retries

### Issue: Data Not Passing Between Nodes
**Solution**: Check connections and ensure node outputs data

## Advanced Patterns

### Rate Limiting
Use Wait node or Schedule trigger with controlled intervals

### Data Deduplication
Store processed IDs in database, check before processing

### Parallel Processing
Use Split in Batches with multiple processing nodes

### State Management
Use database or Redis to maintain workflow state

### Dynamic Workflows
Use HTTP Request to fetch workflow configuration

## Version Control

- Export workflows as JSON
- Store in git repository
- Document changes in commit messages
- Use environments (dev/staging/prod)
- Test before promoting to production

---

This manual represents years of n8n expertise distilled into actionable guidance.
Follow these patterns for production-quality workflows.
"""


def main():
    """Load n8n manual into knowledge base."""
    logger.info("Starting n8n manual embedding process")

    try:
        # Add manual to knowledge base
        doc_id = memory.add_document(
            content=N8N_MANUAL,
            source='manual',
            title='n8n Super User Manual - Expert Knowledge Base',
            url=None,
            meta={'type': 'foundational_knowledge', 'version': '1.0'}
        )

        logger.info("n8n manual loaded successfully", doc_id=doc_id)
        print(f"✓ n8n manual loaded into knowledge base (doc_id: {doc_id})")
        print(f"✓ Document chunked and embedded for semantic search")

        return 0

    except Exception as e:
        logger.error("Failed to load n8n manual", error=str(e))
        print(f"✗ Error loading manual: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
