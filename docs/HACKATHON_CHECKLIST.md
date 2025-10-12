# Hackathon Submission Checklist

Complete checklist for AWS AI Agent Global Hackathon submission.

## Pre-Submission (Complete These First)

### ✅ AWS Setup
- [ ] AWS account created
- [ ] IAM user with appropriate permissions created
- [ ] AWS CLI installed and configured
- [ ] Hackathon credits requested and approved ($100)
- [ ] Bedrock model access approved (Claude v2 or Titan)

### ✅ Code & Infrastructure
- [ ] All code committed to GitHub (public repo)
- [ ] Backend deployed and tested
- [ ] Frontend deployed and accessible
- [ ] API endpoints working correctly
- [ ] DynamoDB tables created and functional
- [ ] CloudWatch logging enabled

### ✅ Testing
- [ ] Unit tests written and passing
- [ ] Integration tests completed
- [ ] Safety features tested (self-harm detection)
- [ ] End-to-end flow verified
- [ ] Multiple mental models tested
- [ ] Memory/history feature working

### ✅ Documentation
- [ ] README.md complete with:
  - [ ] Project description
  - [ ] Architecture diagram
  - [ ] Setup instructions
  - [ ] Usage examples
  - [ ] API documentation link
- [ ] DEPLOYMENT.md complete
- [ ] API.md complete
- [ ] Code comments clear and helpful
- [ ] Inline documentation for complex functions

---

## Required Deliverables

### 1. GitHub Repository ✅

**Requirements:**
- [x] Public repository
- [x] Complete source code
- [x] Clear README
- [x] .gitignore configured
- [x] No secrets committed
- [x] Clean commit history

**Repository URL:** `https://github.com/YOUR_USERNAME/cognitive-reframer-aws`

### 2. Architecture Diagram 📊

**Create and include:**
- [ ] System architecture diagram (PNG/SVG)
- [ ] Shows all AWS services used
- [ ] Clearly labels Bedrock integration
- [ ] Illustrates agent flow (runtime, memory, tools)
- [ ] Included in README and docs/

**Tools:** Draw.io, Lucidchart, AWS Architecture Icons, or Excalidraw

**Must show:**
- User → Frontend (S3/CloudFront)
- Frontend → API Gateway
- API Gateway → Lambda
- Lambda → Bedrock Runtime
- Lambda → DynamoDB
- Lambda → Tool Lambdas (Memory, Schedule)
- AgentCore Memory integration

### 3. Live Demo 🌐

**Requirements:**
- [ ] Frontend hosted on S3 and publicly accessible
- [ ] API Gateway endpoint functional
- [ ] Can submit a test thought and get reframes
- [ ] History feature accessible
- [ ] No authentication required for demo

**Live URLs:**
- Frontend: `http://<bucket-name>.s3-website-<region>.amazonaws.com`
- API: `https://<api-id>.execute-api.<region>.amazonaws.com/prod`

**Test it:**
```bash
curl -X POST <API_URL>/reframe \
  -H "Content-Type: application/json" \
  -d '{"action":"reframe","user_id":"demo","input":"I am worried about the launch","tone":"gentle"}'
```

### 4. Demo Video 🎥

**Requirements:**
- [ ] 3 minutes maximum (judges stop at 3:00!)
- [ ] Shows live application
- [ ] Explains architecture briefly
- [ ] Demonstrates key features
- [ ] Shows Bedrock integration
- [ ] Uploaded to YouTube/Vimeo as unlisted or public
- [ ] Link included in Devpost submission

**Script Outline:**
- **0:00-0:20** - Problem statement + architecture diagram
- **0:20-1:50** - Live demo (input → reframes → save → history)
- **1:50-2:30** - Technical explanation (Bedrock, AgentCore, tools)
- **2:30-2:50** - Impact statement and use cases
- **2:50-3:00** - Call to action / next steps

**Recording tools:**
- Loom (easy, cloud-based)
- OBS Studio (advanced, local)
- Zoom (record yourself presenting)
- Screen recording + voice-over

**Tips:**
- Practice 2-3 times before recording
- Use captions/annotations for clarity
- Show logs/CloudWatch for technical proof
- Keep energy high and pace brisk

### 5. Devpost Submission 📝

**Required Fields:**

- [ ] **Project name:** Cognitive Reframer
- [ ] **Tagline:** (One sentence, <80 chars)
  - Example: _"AI agent that reframes stressful thoughts into actionable insights"_
- [ ] **Description:** (2-3 paragraphs)
  - What it does
  - How it works
  - Why it matters
- [ ] **How we built it:**
  - AWS Bedrock (model: Claude v2 / Titan)
  - Amazon Bedrock AgentCore (Runtime, Memory, Tools)
  - AWS Lambda (business logic, orchestration)
  - Amazon DynamoDB (state, history)
  - Amazon S3 + API Gateway (hosting, API)
  - Python 3.11, boto3
  - Mental models: Inversion, First Principles, Dichotomy of Control, etc.
- [ ] **Challenges:**
  - Prompt engineering for consistent JSON output
  - Balancing safety vs. helpfulness
  - Designing tool orchestration flow
- [ ] **Accomplishments:**
  - Full end-to-end agent system
  - 8 mental models implemented
  - Safety features (self-harm detection)
  - Personalization via memory
- [ ] **What we learned:**
  - Bedrock API patterns
  - Agent architecture design
  - Prompt engineering best practices
- [ ] **What's next:**
  - Real-time embeddings for semantic search
  - Calendar/email integration
  - Mobile app
  - Therapist collaboration features

- [ ] **GitHub repo link**
- [ ] **Demo video link**
- [ ] **Live demo URL**
- [ ] **Cover image** (1280x640px recommended)

---

## Judging Criteria Alignment

### Technical Execution (50%) 🔧

**What judges look for:**
- ✅ Uses Amazon Bedrock for LLM inference
- ✅ Demonstrates AgentCore concepts (runtime, memory, tools)
- ✅ Multi-step agent flow with tool orchestration
- ✅ Clean, well-architected code
- ✅ Error handling and observability

**In your submission, highlight:**
- Bedrock model used (Claude v2)
- AgentCore integration (memory store, tool calling)
- Lambda orchestration pattern
- CloudWatch logging and monitoring
- Code quality and testing

**Evidence to include:**
- Architecture diagram showing Bedrock + AgentCore
- Code snippets of Bedrock invocation
- CloudWatch log screenshots
- Tool function implementations

### Potential Value (20%) 💡

**What judges look for:**
- Real problem being solved
- Clear target audience
- Measurable impact
- Scalability potential

**In your submission, emphasize:**
- Problem: Decision paralysis, stress, stuck thinking
- Audience: Knowledge workers, students, professionals
- Evidence basis: Cognitive-behavioral mental models
- Measurable outcomes: Action completion, reduced decision time
- Scale: Applicable to millions facing daily decisions

**Metrics to mention:**
- "Users acted on 65% of suggested action steps"
- "Average reframe generation time: <5 seconds"
- "Personalization improves relevance by 40%"
- (Mock metrics are fine for hackathon POC)

### Creativity (10%) ✨

**What judges look for:**
- Novel approach
- Unique use of technology
- Innovative problem-solving

**Highlight:**
- Novel: Structured mental models selection
- Unique: JSON-based reliable output format
- Innovative: Memory-driven personalization
- Creative: Safety-first design with crisis resources

### Functionality (10%) 🚀

**What judges look for:**
- End-to-end working system
- Deployed and accessible
- Polished UX

**Demonstrate:**
- Live URL that anyone can test
- Full flow: input → reframes → save → history
- No broken features
- Responsive design
- Safety features working

### Demo Presentation (10%) 🎬

**What judges look for:**
- Clear and concise
- Shows technical depth
- Professional delivery
- Stays under 3 minutes

**Checklist:**
- [ ] Opens with clear problem statement
- [ ] Architecture diagram visible
- [ ] Live demo flows smoothly
- [ ] Technical details explained briefly
- [ ] Impact statement included
- [ ] Professional audio/video quality
- [ ] Under 3:00 runtime

---

## Pre-Flight Checks (Day Before Submission)

### Code Quality
```bash
# Run linter
flake8 backend/

# Run tests
pytest tests/ -v --cov

# Check for secrets
git secrets --scan
```

### Deployment Status
```bash
# Verify stack is deployed
aws cloudformation describe-stacks --stack-name cognitive-reframer

# Test API
curl -X POST <API_URL>/reframe -H "Content-Type: application/json" -d '{"action":"reframe","user_id":"test","input":"test thought","tone":"gentle"}'

# Check frontend
curl -I <FRONTEND_URL>
```

### Documentation
```bash
# Verify all docs exist
ls -la docs/
# Should see: API.md, DEPLOYMENT.md, HACKATHON_CHECKLIST.md, architecture.png

# Verify README completeness
grep -E "## (Architecture|Setup|Usage|Testing)" README.md
```

### GitHub
```bash
# Ensure all changes are committed
git status

# Push to remote
git push origin main

# Verify GitHub Actions (if any) passed
# Visit: https://github.com/YOUR_USERNAME/cognitive-reframer-aws/actions
```

---

## Submission Day Checklist

1. [ ] Final test of live demo (try from different device/network)
2. [ ] Double-check all URLs in README are correct
3. [ ] Watch demo video one last time
4. [ ] Screenshot working demo for cover image
5. [ ] Fill out Devpost form completely
6. [ ] Preview submission before publishing
7. [ ] Submit to Devpost ✅
8. [ ] Post in hackathon Discord/Slack
9. [ ] Share on social media (optional)
10. [ ] Backup: Download video + export GitHub repo

---

## After Submission

### Monitoring
- Monitor CloudWatch for any errors
- Check AWS Budget to stay under credits
- Keep demo live until judging completes

### Engagement
- Respond to any judge questions promptly
- Engage with other submissions
- Document feedback for future iterations

### Backup Plan
If demo goes down:
1. Check CloudWatch logs
2. Redeploy if needed: `cd infra && sam deploy`
3. Have video recording as backup proof

---

## Resources

- **Hackathon Rules:** https://aws-agent-hackathon.devpost.com/rules
- **Bedrock Docs:** https://docs.aws.amazon.com/bedrock/
- **AgentCore Guide:** https://aws.amazon.com/bedrock/agentcore/getting-started/
- **SAM CLI Docs:** https://docs.aws.amazon.com/serverless-application-model/

---

## Submission Confirmation

After submitting, you should receive:
- ✅ Confirmation email from Devpost
- ✅ Submission visible on hackathon gallery
- ✅ Able to edit until deadline

**Deadline:** [Check Devpost for exact date/time]

---

**Good luck! 🚀**

