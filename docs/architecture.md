# Cognitive Reframer Architecture

## System Overview

Cognitive Reframer is a serverless, event-driven AI agent built on AWS that transforms user thoughts into actionable cognitive reframes using evidence-based mental models.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                  │
│                                                                          │
│  ┌──────────────┐                                                       │
│  │   Web UI     │  (Browser)                                           │
│  │  React SPA   │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                                │
└─────────┼────────────────────────────────────────────────────────────────┘
          │ HTTPS
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DELIVERY LAYER                                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Amazon S3 + CloudFront (Static Website Hosting)             │      │
│  │  - index.html, app.js, styles.css                            │      │
│  │  - Global CDN distribution                                   │      │
│  └──────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            API LAYER                                     │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Amazon API Gateway (REST API)                               │      │
│  │  - /reframe  (POST)  → Generate cognitive reframes           │      │
│  │  - /history  (POST)  → Retrieve user history                 │      │
│  │  - /user     (POST)  → Get/create user profile               │      │
│  │  - CORS enabled, rate limiting, request validation           │      │
│  └────────────┬─────────────────────────────────────────────────┘      │
└───────────────┼──────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       COMPUTE / ORCHESTRATION LAYER                      │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  AWS Lambda: ReframeLambda (Main Handler)                  │         │
│  │                                                             │         │
│  │  Flow:                                                      │         │
│  │  1. Validate & sanitize input                              │         │
│  │  2. Safety check (self-harm detection)                     │         │
│  │  3. Call memory_recall tool → get context                  │         │
│  │  4. Build system prompt with mental models                 │         │
│  │  5. Invoke Bedrock Runtime                                 │         │
│  │  6. Parse JSON response                                    │         │
│  │  7. Store reframe via store_reframe tool                   │         │
│  │  8. Return formatted response                              │         │
│  │                                                             │         │
│  │  Environment:                                               │         │
│  │  - Python 3.11 runtime                                     │         │
│  │  - 256 MB memory, 30s timeout                              │         │
│  │  - IAM role: Bedrock invoke, DynamoDB CRUD                 │         │
│  └──────────────┬─────────────────────────────────┬────────────┘         │
│                 │                                 │                      │
│                 │                                 │                      │
│  ┌──────────────▼─────────────┐   ┌──────────────▼─────────────┐       │
│  │ Lambda: MemoryToolLambda   │   │ Lambda: ScheduleToolLambda │       │
│  │                            │   │                            │       │
│  │ Functions:                 │   │ Functions:                 │       │
│  │ - memory_recall()          │   │ - schedule_followup()      │       │
│  │ - memory_store()           │   │ - parse_follow_up_window() │       │
│  │ - memory_search()          │   │                            │       │
│  └────────────┬───────────────┘   └──────────────┬─────────────┘       │
└───────────────┼──────────────────────────────────┼──────────────────────┘
                │                                  │
                ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI / INFERENCE LAYER                             │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Amazon Bedrock Runtime                                      │      │
│  │                                                               │      │
│  │  Model: anthropic.claude-v2 (or amazon.titan-text-express)   │      │
│  │                                                               │      │
│  │  Input: System prompt + user thought + memory context        │      │
│  │  Output: JSON with 2 reframes, explanations, action steps    │      │
│  │                                                               │      │
│  │  Configuration:                                               │      │
│  │  - max_tokens: 1024                                          │      │
│  │  - temperature: 0.3 (deterministic)                          │      │
│  │  - top_p: 0.9                                                │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  Amazon Bedrock AgentCore (Conceptual Integration)           │      │
│  │                                                               │      │
│  │  Components Used:                                             │      │
│  │  - Runtime: Orchestration of LLM + tools                     │      │
│  │  - Memory: Vector store for past reframes (planned)          │      │
│  │  - Gateway: Tool registration and invocation (planned)       │      │
│  │                                                               │      │
│  │  Current Implementation:                                      │      │
│  │  - Lambda-based orchestrator (emulates AgentCore Runtime)    │      │
│  │  - DynamoDB for memory (will migrate to AgentCore Memory)    │      │
│  │  - Direct Lambda tool calls (will use AgentCore Gateway)     │      │
│  └──────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA / STORAGE LAYER                            │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  Amazon DynamoDB                                            │         │
│  │                                                             │         │
│  │  Tables:                                                    │         │
│  │                                                             │         │
│  │  1. CognitiveReframer-Reframes                             │         │
│  │     - PK: reframe_id (string)                              │         │
│  │     - Attributes: user_id, source_input, models_used,      │         │
│  │       reframes (JSON), summary, created_at, ttl            │         │
│  │     - GSI: UserIdIndex (user_id + created_at)              │         │
│  │                                                             │         │
│  │  2. CognitiveReframer-Users                                │         │
│  │     - PK: user_id (string)                                 │         │
│  │     - Attributes: display_name, preferences (JSON),        │         │
│  │       created_at                                            │         │
│  │                                                             │         │
│  │  3. CognitiveReframer-Reminders                            │         │
│  │     - PK: reminder_id (string)                             │         │
│  │     - Attributes: user_id, reframe_id, scheduled_time,     │         │
│  │       method, status                                        │         │
│  │     - GSI: UserIdIndex (user_id)                           │         │
│  │                                                             │         │
│  │  Configuration:                                             │         │
│  │  - Billing: Pay-per-request (on-demand)                    │         │
│  │  - Encryption: At-rest enabled                             │         │
│  │  - TTL: 90 days on Reframes table                          │         │
│  │  - Streams: Enabled for potential event-driven workflows   │         │
│  └────────────────────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY / MONITORING LAYER                    │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────┐         │
│  │  Amazon CloudWatch                                          │         │
│  │                                                             │         │
│  │  Log Groups:                                                │         │
│  │  - /aws/lambda/CognitiveReframer-Main                      │         │
│  │  - /aws/lambda/CognitiveReframer-MemoryTool                │         │
│  │  - /aws/lambda/CognitiveReframer-ScheduleTool              │         │
│  │  - /aws/apigateway/cognitive-reframer-api                  │         │
│  │                                                             │         │
│  │  Metrics:                                                   │         │
│  │  - Lambda invocations, errors, duration                    │         │
│  │  - API Gateway 4xx/5xx errors, latency                     │         │
│  │  - DynamoDB consumed capacity, throttles                   │         │
│  │  - Bedrock invocation count, token usage                   │         │
│  │                                                             │         │
│  │  Alarms:                                                    │         │
│  │  - Budget alert at $25                                     │         │
│  │  - Lambda error rate > 5%                                  │         │
│  │  - API latency > 10s                                       │         │
│  └────────────────────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Reframe Generation Flow

1. **User Input**
   - User enters thought in frontend (1-500 chars)
   - Selects tone: gentle or direct
   - Clicks "Generate Reframes"

2. **API Request**
   - Frontend sends POST to `/reframe`
   - Payload: `{action, user_id, input, tone}`
   - API Gateway validates and forwards to Lambda

3. **Lambda Orchestration**
   - **Validation**: Check input length, sanitize
   - **Safety**: Screen for self-harm keywords
     - If detected → return crisis resources
   - **Memory Recall**: Query DynamoDB for past reframes (top 3)
   - **Prompt Construction**: Build system prompt with:
     - 8 mental models definitions
     - Memory context (past reframes)
     - Tone guidance
     - Few-shot examples
   - **Bedrock Invocation**: Send prompt to Bedrock
   - **Response Parsing**: Extract JSON from model output
   - **Validation**: Ensure required fields present
   - **Storage**: Save reframe to DynamoDB
   - **Response**: Return formatted JSON to frontend

4. **Frontend Rendering**
   - Display two reframes side-by-side
   - Show action steps as ordered lists
   - Display summary
   - Enable Save and Schedule buttons

### Memory System

**Current Implementation (DynamoDB)**
- Store reframes with metadata
- Query by user_id + timestamp
- Return top-k most recent for context

**Planned (AgentCore Memory)**
- Generate embeddings for semantic search
- Store in AgentCore vector memory
- Retrieve similar reframes by meaning, not recency

### Tool System

**Memory Tool**
- `memory_recall(user_id, query, top_k)` → returns relevant past reframes
- `memory_store(user_id, reframe_data)` → saves new reframe
- `memory_search(user_id, query)` → semantic search (future)

**Schedule Tool**
- `schedule_followup(user_id, reframe_id, hours)` → creates reminder
- Stores in Reminders table
- Future: Trigger SNS/email at scheduled time

## Security Architecture

### Authentication & Authorization
- **Current**: Demo mode (no auth)
- **Production Plan**: Amazon Cognito user pools
  - OAuth 2.0 / OpenID Connect
  - JWT tokens for API access
  - IAM role-based access

### Data Security
- **In-transit**: HTTPS/TLS 1.2+ for all API calls
- **At-rest**: DynamoDB encryption enabled
- **Secrets**: Environment variables (no hardcoded credentials)
- **IAM**: Least-privilege roles for Lambda
- **Input validation**: Length limits, sanitization
- **Content safety**: Self-harm keyword detection

### Privacy
- No PII storage (user IDs are opaque)
- 90-day TTL on reframes (auto-deletion)
- No logging of sensitive content
- Clear disclaimers (not therapy)

## Scalability

### Current Capacity
- **API Gateway**: 10,000 requests/second (default)
- **Lambda**: 1,000 concurrent executions (default)
- **DynamoDB**: Unlimited (on-demand mode)
- **Bedrock**: Model-specific quotas (check console)

### Scaling Strategy
- **Horizontal**: Lambda auto-scales
- **DynamoDB**: On-demand auto-scales
- **Caching**: Add CloudFront in front of S3
- **Rate limiting**: API Gateway throttling
- **Cost optimization**: Use Claude Instant for lower-priority requests

### Performance Targets
- API latency: < 5 seconds (p95)
- Bedrock response: < 3 seconds
- Frontend load: < 2 seconds
- Memory recall: < 100ms

## Cost Breakdown

**Estimated Monthly Cost (1,000 users, 10 reframes each)**

| Service | Usage | Cost |
|---------|-------|------|
| Bedrock (Claude v2) | 10K invocations × 512 tokens | $120 |
| Lambda | 10K invocations, 3s avg | $0.20 |
| API Gateway | 10K requests | $0.04 |
| DynamoDB | 10GB storage, 100K reads, 10K writes | $3.50 |
| S3 + Data Transfer | 10GB storage, 100GB transfer | $2.00 |
| CloudWatch | 10GB logs | $5.00 |
| **Total** | | **~$131/month** |

**Cost Optimization:**
- Use Claude Instant instead of v2: 80% cheaper
- Cache common responses
- Implement request batching
- Set DynamoDB TTL (already enabled)
- Use S3 Intelligent-Tiering

## AgentCore Integration Roadmap

### Phase 1: Current (Lambda Orchestrator)
- [x] Direct Bedrock invocation
- [x] Lambda-based tool calling
- [x] DynamoDB for memory

### Phase 2: AgentCore Runtime
- [ ] Migrate orchestration to AgentCore Runtime
- [ ] Register Lambda tools with AgentCore Gateway
- [ ] Use AgentCore tool invocation patterns

### Phase 3: AgentCore Memory
- [ ] Generate embeddings (Bedrock Titan Embeddings)
- [ ] Store in AgentCore Vector Memory
- [ ] Semantic similarity search for context retrieval

### Phase 4: Advanced Features
- [ ] Multi-turn conversations (session state)
- [ ] Streaming responses (Bedrock streaming API)
- [ ] A/B testing of mental model selection strategies
- [ ] Human-in-the-loop for model selection feedback

## Mental Model Selection Algorithm

**Current: Deterministic (Prompt-Based)**
- LLM selects 2 models based on input analysis
- Guided by examples in system prompt
- Temperature 0.3 for consistency

**Future: Hybrid Approach**
1. **Keyword extraction** from input
2. **Model scoring** based on keyword → model mapping
3. **Top-2 selection** by score
4. **LLM application** of selected models to generate reframes

**Model → Use Case Mapping:**
- **Inversion**: Fear of failure, worst-case thinking
- **First Principles**: Complex decisions, confusion
- **Dichotomy of Control**: Anxiety, external dependencies
- **5 Whys**: Unclear root cause, procrastination
- **Outcome Forecasting**: Catastrophizing, uncertainty
- **Cost-Benefit**: Trade-off decisions, comparisons
- **Scaling**: Overwhelm, perspective needed
- **Premortem**: Risk assessment, preparation

## Disaster Recovery

### Backup Strategy
- **DynamoDB**: Point-in-time recovery enabled
- **Code**: Version-controlled in GitHub
- **Configuration**: Infrastructure-as-code (SAM template)

### Failover Plan
- **Lambda**: Multi-AZ by default
- **DynamoDB**: Global tables (future)
- **S3**: Cross-region replication (if needed)

### Monitoring & Alerts
- CloudWatch alarms on error rates
- Budget alerts for cost overruns
- Dead letter queues for failed invocations

## Future Architecture Enhancements

1. **Real-time Collaboration**
   - WebSocket API (API Gateway WebSocket)
   - Live updates when reframes are generated
   - Shared sessions for teams

2. **Multi-modal Input**
   - Voice input (Amazon Transcribe)
   - Image context (Amazon Rekognition)
   - Video analysis (Amazon Kinesis Video Streams)

3. **Personalization Engine**
   - User preference learning
   - Model selection optimization
   - Adaptive tone adjustment

4. **Integration Ecosystem**
   - Slack bot
   - Google Calendar plugin
   - Notion/Obsidian integration
   - Email digests (Amazon SES)

5. **Enterprise Features**
   - Team dashboards
   - Admin controls
   - SSO (SAML/OIDC)
   - Compliance logging

---

**Diagram Tools:**
- AWS Architecture Icons: https://aws.amazon.com/architecture/icons/
- Draw.io: https://app.diagrams.net/
- Lucidchart: https://www.lucidchart.com/
- Excalidraw: https://excalidraw.com/

