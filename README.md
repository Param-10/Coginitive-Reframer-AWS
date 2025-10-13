# Cognitive Reframer

**An autonomous AWS Bedrock Agent that transforms stuck or stressful thoughts into evidence-backed cognitive reframes with actionable steps.**

[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange)](https://aws.amazon.com/bedrock/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Hackathon Submission:** AWS AI Agent Global Hackathon - Best Amazon Bedrock AgentCore Implementation

---

## 🎯 What It Does

Cognitive Reframer is an intelligent agent that:

1. **Analyzes** your stuck or stressful thought using evidence-based mental models
2. **Generates** two distinct cognitive reframes from different perspectives
3. **Provides** 2-3 concrete micro-actions you can take in 10-30 minutes
4. **Remembers** your past reframes to personalize future suggestions
5. **Schedules** optional follow-up reminders to check your progress

### Example Flow

**Input:** *"I'm sure the launch will fail and it'll be a disaster."*

**Agent Response:**
- **Model 1 (Inversion):** "Instead of imagining failure, list the fastest ways to fail and stop doing those things."
  - Action steps: List top 3 failure modes, assign mitigations, schedule check-in
- **Model 2 (Dichotomy of Control):** "Separate what you control from what you don't. Focus on the controllables first."
  - Action steps: Block 2 hours for high-impact task, email stakeholders for clarity

---

## 🏗️ Architecture

```
[User UI] → [CloudFront/S3] → [API Gateway] → [Lambda Handler]
                                                     ↓
                                     ┌───────────────┴──────────────┐
                                     ↓                              ↓
                            [Bedrock Runtime]              [Tool Lambdas]
                              (Claude v2)                    (Memory, Schedule)
                                     ↓                              ↓
                            [AgentCore Memory]            [DynamoDB Tables]
```

### AWS Services Used

- **Amazon Bedrock** - LLM inference (Claude v2/Titan)
- **Amazon Bedrock AgentCore** - Runtime, Memory, Tools
- **AWS Lambda** - Business logic and tool implementations
- **Amazon API Gateway** - REST API endpoints
- **Amazon DynamoDB** - User profiles, reframes, reminders
- **Amazon S3** - Static frontend hosting
- **Amazon CloudWatch** - Logging and observability
- **Amazon SNS** - Follow-up notifications (optional)

---

## 🧠 Mental Models Implemented

The agent selects from 8 evidence-backed cognitive models:

1. **Inversion** - Think backward: what guarantees failure? Avoid that.
2. **First Principles** - Break down to fundamental truths; rebuild reasoning.
3. **Dichotomy of Control** - Separate controllables from uncontrollables.
4. **5 Whys** - Ask "why" repeatedly to find root causes.
5. **Outcome Forecasting** - Project realistic best/worst/likely scenarios.
6. **Cost-Benefit** - Explicitly compare costs vs. benefits.
7. **Scaling** - Break big problems down or expand perspective.
8. **Premortem** - Imagine failure happened; work backward to prevent it.

---

## 📁 Project Structure

```
/cognitive-reframer
├── backend/
│   ├── lambda_reframe/
│   │   ├── app.py                 # Main Lambda handler
│   │   └── requirements.txt
│   └── tools/
│       ├── memory_tool.py         # Memory recall/storage tool
│       ├── schedule_tool.py       # Follow-up scheduling tool
│       └── requirements.txt
├── frontend/
│   ├── index.html                 # Single-page UI
│   ├── app.js                     # Frontend logic
│   └── styles.css                 # Styling
├── infra/
│   ├── template.yaml              # AWS SAM template
│   └── deploy.sh                  # Deployment script
├── tests/
│   ├── test_reframe.py           # Unit tests
│   └── mock_responses.json       # Mock Bedrock responses
├── docs/
│   └── architecture.png          # Architecture diagram
├── README.md
└── .gitignore
```

---

## 🚀 Quick Start

### Prerequisites

- AWS Account with Bedrock access ([request here](https://console.aws.amazon.com/bedrock))
- AWS CLI configured with IAM credentials
- Python 3.11+
- AWS SAM CLI (for deployment)
- Hackathon credits requested via Devpost

### 1. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/cognitive-reframer-aws.git
cd cognitive-reframer-aws

# Install AWS SAM CLI
pip install aws-sam-cli

# Configure AWS credentials
aws configure
```

### 2. Request Bedrock Model Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Navigate to **Model access**
3. Request access to **Anthropic Claude v2** or **Amazon Titan Text Express**
4. Wait for approval (usually instant for Titan, may take hours for Claude)

### 3. Deploy Infrastructure

```bash
# Build and deploy using SAM
cd infra
sam build
sam deploy --guided

# Follow prompts:
# - Stack Name: cognitive-reframer
# - AWS Region: us-east-1 (or your preferred region)
# - Confirm all defaults

# Note the API URL from outputs
```

### 4. Deploy Frontend

```bash
# Get your S3 bucket name from CloudFormation outputs
export BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name cognitive-reframer \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucket`].OutputValue' \
  --output text)

# Update API URL in frontend/app.js
export API_URL=$(aws cloudformation describe-stacks \
  --stack-name cognitive-reframer \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

sed -i '' "s|API_ENDPOINT_PLACEHOLDER|$API_URL|g" frontend/app.js

# Upload frontend files
aws s3 sync frontend/ s3://$BUCKET_NAME/ --acl public-read

# Get website URL
echo "Frontend URL: http://$BUCKET_NAME.s3-website-us-east-1.amazonaws.com"
```

### 5. Test Locally (Optional)

```bash
# Run unit tests
cd tests
pytest test_reframe.py -v

# Test Lambda locally with SAM
sam local invoke ReframeLambda -e test_event.json
```

---

## 🔧 Configuration

### Environment Variables

Set these in AWS Lambda console or `template.yaml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION` | AWS region for services | `us-east-1` |
| `BEDROCK_MODEL_ID` | Bedrock model to use | `anthropic.claude-v2` |
| `REFRAMES_TABLE` | DynamoDB reframes table | `CognitiveReframer-Reframes` |
| `USERS_TABLE` | DynamoDB users table | `CognitiveReframer-Users` |
| `REMINDERS_TABLE` | DynamoDB reminders table | `CognitiveReframer-Reminders` |

### Model Selection

**Currently Deployed:** `amazon.titan-text-express-v1` ✅

Supported Bedrock models:
- `amazon.titan-text-express-v1` (currently deployed - AWS native, working)
- `anthropic.claude-3-5-sonnet-20240620-v1:0` (upgrade when access approved)
- `anthropic.claude-3-haiku-20240307-v1:0` (fast and cheap)
- `anthropic.claude-v2` (legacy support)

To change model: Edit `infra/template.yaml` line 90, then redeploy with `sam deploy`.

---

## 📖 API Documentation

### POST `/reframe`

Generate cognitive reframes for a thought.

**Request:**
```json
{
  "action": "reframe",
  "user_id": "user123",
  "input": "I'll embarrass myself in the meeting",
  "tone": "gentle"
}
```

**Response:**
```json
{
  "reframe_id": "user123_1234567890",
  "user_id": "user123",
  "created_at": "2025-01-15T10:30:00Z",
  "input": "I'll embarrass myself in the meeting",
  "model_selection": ["Premortem", "Scaling"],
  "reframes": [
    {
      "model": "Premortem",
      "reframe": "Imagine the meeting went badly—what specifically happened? Prepare for those scenarios now.",
      "explanation": "Premortem identifies concrete risks ahead of time so you can address them proactively.",
      "action_steps": [
        "List 3 things that could go wrong",
        "Rehearse responses for 10 minutes",
        "Prepare a fallback line"
      ]
    },
    {
      "model": "Scaling",
      "reframe": "Zoom out: how important will this meeting feel in 6 months?",
      "explanation": "Scaling reduces emotional weight by expanding time perspective.",
      "action_steps": [
        "Write one learning goal (not perfection)",
        "Recall a past scary meeting that turned out fine"
      ]
    }
  ],
  "summary": "Prepare for realistic scenarios and remember this is one step in a journey.",
  "follow_up": "24 hours"
}
```

### POST `/history`

Retrieve user's reframe history.

**Request:**
```json
{
  "action": "history",
  "user_id": "user123"
}
```

**Response:**
```json
{
  "user_id": "user123",
  "history": [
    {
      "reframe_id": "user123_1234567890",
      "source_input": "I'll embarrass myself",
      "models_used": ["Premortem", "Scaling"],
      "summary": "Prepare and zoom out",
      "created_at": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

## 🧪 Testing

### Unit Tests

```bash
cd tests
pytest test_reframe.py -v --cov=../backend
```

### Integration Tests

```bash
# Test full flow with mock Bedrock
python tests/integration_test.py
```

### Load Testing

```bash
# Use locust or artillery for load testing
artillery quick --count 10 --num 50 $API_URL/reframe
```

---

## 🔒 Security & Safety

### Content Safety

- **Self-harm detection**: Inputs are screened for crisis keywords
- **Crisis resources**: System provides emergency contact info when needed
- **Not therapy**: Clear disclaimers that this is a cognitive tool, not medical advice

### AWS Security

- **IAM roles**: Lambda functions use least-privilege IAM roles
- **No hardcoded credentials**: All secrets via IAM or Parameter Store
- **API rate limiting**: Configured in API Gateway
- **DynamoDB encryption**: At-rest encryption enabled
- **CORS**: Properly configured for frontend domain

---

## 💰 Cost Estimates

With hackathon $100 credits:

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| Bedrock (Claude v2) | 1000 invocations @ 512 tokens | ~$12 |
| Lambda | 1000 invocations | ~$0.20 |
| DynamoDB | 10GB storage, 1M reads/writes | ~$2.50 |
| API Gateway | 1000 requests | ~$0.01 |
| S3 + CloudFront | Static hosting | ~$0.50 |
| **Total** | | **~$15/month** |

### Cost Optimization

- Use `claude-instant-v1` for dev (cheaper)
- Set DynamoDB on-demand pricing
- Enable CloudWatch log expiration
- Set AWS Budget alerts at $25

---

## 📊 Observability

### CloudWatch Logs

View logs in AWS Console:
```bash
aws logs tail /aws/lambda/CognitiveReframer-Main --follow
```

### Metrics Dashboard

Key metrics tracked:
- Bedrock invocation latency
- JSON parse success rate
- Memory recall hit rate
- User engagement (history queries)

Access at: CloudWatch → Dashboards → CognitiveReframer

---

## 🎥 Demo Video

[3-Minute Demo Video](https://youtu.be/YOUR_VIDEO_ID)

**Highlights:**
- Live reframing demonstration
- Memory personalization in action
- Architecture walkthrough
- CloudWatch logs showing Bedrock calls

---

## 🏆 Hackathon Criteria Alignment

### Technical Execution (50%)
✅ Uses Amazon Bedrock for LLM inference  
✅ Implements AgentCore Runtime concepts (memory, tools)  
✅ Multi-step agent flow with tool orchestration  
✅ Production-ready architecture with observability  

### Potential Value (20%)
✅ Addresses real problem (decision paralysis, stress)  
✅ Evidence-based mental models  
✅ Measurable outcomes (action completion rate)  

### Creativity (10%)
✅ Novel application of mental models  
✅ JSON-structured outputs for reliability  
✅ Personalization via memory  

### Functionality (10%)
✅ Full end-to-end working demo  
✅ Live deployed frontend + backend  
✅ Error handling and safety features  

### Demo Presentation (10%)
✅ Clear 3-minute video  
✅ Architecture diagram  
✅ Live system demonstration  

---

## 🛣️ Roadmap

### Phase 1 (Current - Hackathon MVP)
- [x] Core reframing engine
- [x] 8 mental models
- [x] DynamoDB persistence
- [x] Basic frontend
- [x] Safety filters

### Phase 2 (Post-Hackathon)
- [ ] AgentCore vector memory integration
- [ ] Real-time embeddings for semantic search
- [ ] Calendar integration (Google/Outlook)
- [ ] SMS reminders via SNS
- [ ] User authentication (Cognito)

### Phase 3 (Future)
- [ ] Mobile app (React Native)
- [ ] Slack/Teams integration
- [ ] Multi-language support
- [ ] Therapist collaboration features
- [ ] Analytics dashboard

---

## 🤝 Contributing

This project was built for the AWS AI Agent Global Hackathon. Contributions welcome post-hackathon!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Built with [Amazon Bedrock](https://aws.amazon.com/bedrock/) and [AgentCore](https://aws.amazon.com/bedrock/agentcore/)
- Mental models inspired by research in cognitive behavioral therapy and systems thinking
- Special thanks to AWS for hackathon credits and documentation

---

## 📞 Contact

**Developer:** Your Name  
**Email:** your.email@example.com  
**Project:** [GitHub Repository](https://github.com/YOUR_USERNAME/cognitive-reframer-aws)  
**Demo:** [Live Demo](http://your-bucket.s3-website-us-east-1.amazonaws.com)

---

## ⚠️ Important Disclaimers

**This is not therapy.** Cognitive Reframer is a cognitive toolkit for everyday decision-making and stress management. It is not a substitute for professional mental health care.

**Crisis resources:** If you're experiencing a mental health crisis:
- US: National Suicide Prevention Lifeline: 988
- US: Crisis Text Line: Text HOME to 741741
- International: https://www.iasp.info/resources/Crisis_Centres/

---

**Built for AWS AI Agent Global Hackathon 2025** 🚀

---

## 🌐 Live Demo

**Frontend:** http://cognitive-reframer-frontend-374666742520.s3-website-us-east-1.amazonaws.com  
**API Endpoint:** https://nw0ktqzscb.execute-api.us-east-1.amazonaws.com/prod  
**AWS Region:** us-east-1  
**Status:** ✅ Deployed and Operational  

---

## ⚡ Quick Test

```bash
curl -X POST https://nw0ktqzscb.execute-api.us-east-1.amazonaws.com/prod/reframe \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reframe",
    "user_id": "demo",
    "input": "I am worried about my presentation tomorrow",
    "tone": "gentle"
  }'
```
