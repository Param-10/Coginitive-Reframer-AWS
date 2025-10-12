# API Documentation

Complete API reference for Cognitive Reframer backend endpoints.

## Base URL

```
https://<api-id>.execute-api.<region>.amazonaws.com/prod
```

Replace `<api-id>` and `<region>` with values from CloudFormation outputs.

## Authentication

Currently uses demo mode with user IDs. For production, add API keys or Cognito authentication.

## Endpoints

### POST /reframe

Generate cognitive reframes for a user's thought.

**Request:**

```json
{
  "action": "reframe",
  "user_id": "string",
  "input": "string (1-500 characters)",
  "tone": "gentle" | "direct"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| action | string | Yes | Must be "reframe" |
| user_id | string | Yes | Unique user identifier |
| input | string | Yes | User's thought (1-500 chars) |
| tone | string | No | Response tone: "gentle" or "direct" (default: "gentle") |

**Response (Success):**

```json
{
  "reframe_id": "user123_1705320000000",
  "user_id": "user123",
  "created_at": "2025-01-15T10:00:00Z",
  "input": "I'm worried about the presentation",
  "model_selection": ["Premortem", "Scaling"],
  "reframes": [
    {
      "model": "Premortem",
      "reframe": "Imagine it went badly—what happened? Prepare for that now.",
      "explanation": "Premortem identifies risks proactively.",
      "action_steps": [
        "List 3 things that could go wrong",
        "Rehearse responses for 10 minutes",
        "Prepare a fallback line"
      ]
    },
    {
      "model": "Scaling",
      "reframe": "How important is this in 6 months?",
      "explanation": "Scaling reduces emotional weight.",
      "action_steps": [
        "Write one learning goal",
        "Remember a past success"
      ]
    }
  ],
  "summary": "Prepare for scenarios and keep perspective.",
  "follow_up": "24 hours"
}
```

**Response (Safety Trigger):**

```json
{
  "safety_response": true,
  "message": "Your message suggests you may be in distress...",
  "resources": [
    "National Suicide Prevention Lifeline: 988 (US)",
    "Crisis Text Line: Text HOME to 741741 (US)",
    "International: https://www.iasp.info/resources/Crisis_Centres/"
  ]
}
```

**Status Codes:**

- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `500 Internal Server Error` - Server error

**Example cURL:**

```bash
curl -X POST https://api-url/prod/reframe \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reframe",
    "user_id": "user123",
    "input": "I cannot decide which job to take",
    "tone": "direct"
  }'
```

---

### POST /history

Retrieve user's reframe history.

**Request:**

```json
{
  "action": "history",
  "user_id": "string"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| action | string | Yes | Must be "history" |
| user_id | string | Yes | Unique user identifier |

**Response:**

```json
{
  "user_id": "user123",
  "history": [
    {
      "reframe_id": "user123_1705320000000",
      "source_input": "I'm worried about the presentation",
      "models_used": ["Premortem", "Scaling"],
      "summary": "Prepare and keep perspective",
      "created_at": "2025-01-15T10:00:00Z",
      "reframes": [...]
    }
  ]
}
```

**Status Codes:**

- `200 OK` - Success (empty array if no history)
- `500 Internal Server Error` - Server error

**Example cURL:**

```bash
curl -X POST https://api-url/prod/history \
  -H "Content-Type: application/json" \
  -d '{
    "action": "history",
    "user_id": "user123"
  }'
```

---

### POST /user

Get or create user profile.

**Request:**

```json
{
  "action": "get_user",
  "user_id": "string"
}
```

**Response:**

```json
{
  "user_id": "user123",
  "display_name": "User 123",
  "created_at": "2025-01-15T10:00:00Z",
  "preferences": {
    "default_tone": "gentle",
    "timezone": "UTC"
  }
}
```

**Status Codes:**

- `200 OK` - User found or created
- `500 Internal Server Error` - Server error

---

## Mental Models

The agent selects from these 8 models:

| Model | Description | Best For |
|-------|-------------|----------|
| **Inversion** | Think backward: what guarantees failure? | Avoiding errors |
| **First Principles** | Break down to fundamental truths | Complex decisions |
| **Dichotomy of Control** | Separate controllables from uncontrollables | Anxiety reduction |
| **5 Whys** | Ask "why" repeatedly to find root cause | Problem diagnosis |
| **Outcome Forecasting** | Project realistic scenarios | Catastrophizing |
| **Cost-Benefit** | Explicit comparison of trade-offs | Decision-making |
| **Scaling** | Break down or expand perspective | Overwhelm |
| **Premortem** | Imagine failure, work backward | Risk mitigation |

---

## Error Handling

### Error Response Format

```json
{
  "error": "string",
  "message": "string (optional)",
  "details": {} (optional)
}
```

### Common Errors

**Empty Input**
```json
{
  "error": "Input cannot be empty"
}
```

**Input Too Long**
```json
{
  "error": "Input too long (max 500 characters)"
}
```

**Bedrock Error**
```json
{
  "error": "Failed to invoke Bedrock: <details>"
}
```

**Invalid JSON Response**
```json
{
  "error": "Model returned invalid JSON: <details>"
}
```

---

## Rate Limits

Current limits (can be adjusted in API Gateway):

- **Requests per second:** 10
- **Burst capacity:** 20
- **Daily quota:** 10,000 (hackathon limit)

Exceeding limits returns:
```json
{
  "message": "Too Many Requests"
}
```
Status: `429 Too Many Requests`

---

## CORS Headers

All responses include CORS headers:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
Access-Control-Allow-Headers: Content-Type,X-Amz-Date,Authorization,X-Api-Key
```

For production, restrict `Allow-Origin` to your domain.

---

## Webhooks & Events

### Future: Follow-up Reminders

When scheduling is implemented:

```json
POST /schedule
{
  "user_id": "user123",
  "reframe_id": "user123_1705320000000",
  "hours_from_now": 48,
  "method": "email" | "sms" | "notification"
}
```

---

## SDK Examples

### Python

```python
import requests

API_URL = "https://your-api-url/prod"

def reframe_thought(user_id, thought, tone="gentle"):
    response = requests.post(
        f"{API_URL}/reframe",
        json={
            "action": "reframe",
            "user_id": user_id,
            "input": thought,
            "tone": tone
        }
    )
    return response.json()

result = reframe_thought("user123", "I'm stuck on this decision")
print(result["reframes"])
```

### JavaScript

```javascript
const API_URL = "https://your-api-url/prod";

async function reframeThought(userId, thought, tone = "gentle") {
    const response = await fetch(`${API_URL}/reframe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            action: "reframe",
            user_id: userId,
            input: thought,
            tone: tone
        })
    });
    return await response.json();
}

const result = await reframeThought("user123", "I'm worried about failing");
console.log(result.reframes);
```

---

## Testing

### Test Data

Use these sample inputs for testing:

```json
[
  "I'm sure the launch will fail",
  "I can't decide which job to take",
  "Everyone will realize I'm a fraud",
  "I keep procrastinating on this task",
  "I'm worried about the presentation"
]
```

### Mock Mode

For local testing without Bedrock:

Set environment variable:
```bash
export MOCK_BEDROCK=true
```

Returns predefined responses from `tests/mock_responses.json`.

---

## Versioning

Current API version: **v1** (implicit in `/prod` stage)

Future versions will use explicit versioning:
- `/v1/reframe`
- `/v2/reframe`

---

## Support

Questions or issues?
- GitHub Issues: [repository-url]/issues
- Documentation: [repository-url]/docs
- Hackathon Discord: [link]

