# Quick Start Guide

Get Cognitive Reframer running in 15 minutes.

## Prerequisites Checklist

- [ ] AWS account created
- [ ] AWS CLI installed (`aws --version`)
- [ ] AWS SAM CLI installed (`sam --version`)
- [ ] Configured AWS credentials (`aws configure`)
- [ ] Python 3.11+ installed
- [ ] Hackathon credits requested (optional but recommended)

## Step-by-Step Setup

### 1. Request Bedrock Access (5 minutes)

```bash
# Open Bedrock console
open https://console.aws.amazon.com/bedrock

# Navigate to: Model access → Manage model access
# Request access to:
#   ✓ Anthropic Claude v2 (recommended)
#   ✓ Amazon Titan Text Express v1 (backup)
# Click "Save changes"
```

**Wait for approval** (instant for Titan, may take hours for Claude)

### 2. Deploy Backend (5 minutes)

```bash
# Navigate to infra directory
cd /Users/paramveer/Coginitive-Reframer-AWS/infra

# Run automated deployment
./deploy.sh

# If first time, answer prompts:
# - Stack name: cognitive-reframer
# - Region: us-east-1
# - Confirm changes: Y
# - Allow IAM creation: Y
# - Save config: Y
```

**Save the outputs** (API URL, Frontend URL, Bucket name)

### 3. Test API (2 minutes)

```bash
# Set your API URL from deployment output
export API_URL="https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod"

# Test user endpoint
curl -X POST $API_URL/user \
  -H "Content-Type: application/json" \
  -d '{"action":"get_user","user_id":"test_user"}'

# Should return: {"user_id":"test_user",...}

# Test reframe endpoint
curl -X POST $API_URL/reframe \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reframe",
    "user_id": "test_user",
    "input": "I am worried about the presentation tomorrow",
    "tone": "gentle"
  }'

# Should return: {"reframe_id":..., "reframes":[...], ...}
```

### 4. Open Frontend (1 minute)

```bash
# Get frontend URL from deployment output
# Or retrieve it:
aws cloudformation describe-stacks \
  --stack-name cognitive-reframer \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
  --output text

# Open in browser
open $(aws cloudformation describe-stacks \
  --stack-name cognitive-reframer \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
  --output text)
```

### 5. Test End-to-End (2 minutes)

In the browser:
1. Enter a thought: _"I'm worried the launch will fail"_
2. Select tone: **Gentle**
3. Click **Generate Reframes**
4. Wait 3-5 seconds
5. Verify you see:
   - Two different reframes
   - Action steps for each
   - Summary at the bottom
6. Click **Save to Memory**
7. Switch to **History** tab
8. Verify your reframe appears

## Common Issues & Fixes

### Issue: Bedrock Access Denied

```
Error: User is not authorized to perform: bedrock:InvokeModel
```

**Fix:**
1. Check Bedrock console for model access approval
2. Verify IAM role has `bedrock:InvokeModel` permission
3. Try Titan model if Claude not approved yet:
   - Edit `infra/template.yaml`
   - Change `BEDROCK_MODEL_ID` to `amazon.titan-text-express-v1`
   - Redeploy: `sam deploy`

### Issue: Lambda Timeout

```
Error: Task timed out after 30.00 seconds
```

**Fix:**
```yaml
# Edit infra/template.yaml
Globals:
  Function:
    Timeout: 60  # Increase from 30 to 60

# Redeploy
cd infra && sam deploy
```

### Issue: Frontend 403 Forbidden

**Fix:**
```bash
# Check bucket policy
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name cognitive-reframer \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucket`].OutputValue' \
  --output text)

aws s3api get-bucket-policy --bucket $BUCKET_NAME

# If missing, redeploy stack
cd infra && sam deploy
```

### Issue: API Returns 500 Error

**Fix:**
```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/CognitiveReframer-Main --follow

# Look for error messages
# Common causes:
# - Bedrock model not available
# - DynamoDB table not found
# - Invalid JSON parsing
```

## Next Steps

### Local Development

```bash
# Install dependencies
cd backend/lambda_reframe
pip install -r requirements.txt

# Run unit tests
cd ../../tests
pip install -r requirements.txt
pytest test_reframe.py -v
```

### Monitor Costs

```bash
# Check current spending
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Set up billing alert
aws cloudwatch put-metric-alarm \
  --alarm-name cognitive-reframer-budget \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 25 \
  --comparison-operator GreaterThanThreshold
```

### View Logs

```bash
# Real-time logs
aws logs tail /aws/lambda/CognitiveReframer-Main --follow

# Recent errors only
aws logs filter-log-events \
  --log-group-name /aws/lambda/CognitiveReframer-Main \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '1 hour ago' +%s)000
```

### Update Code

```bash
# After making changes to backend
cd infra
sam build
sam deploy

# After making changes to frontend
cd ../frontend
export BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name cognitive-reframer \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucket`].OutputValue' \
  --output text)
aws s3 sync . s3://$BUCKET_NAME/
```

## Testing Checklist

- [ ] API health check passes
- [ ] Reframe generation works
- [ ] Two different mental models returned
- [ ] Action steps are specific and actionable
- [ ] Summary is coherent
- [ ] Save to memory works
- [ ] History retrieval works
- [ ] Self-harm input shows safety message
- [ ] Input validation rejects empty/too-long input
- [ ] Frontend loads without errors
- [ ] Responsive on mobile

## Performance Benchmarks

Expected performance:
- **API latency (p95):** < 5 seconds
- **Bedrock response:** < 3 seconds  
- **Memory recall:** < 100ms
- **Frontend load:** < 2 seconds

Test performance:
```bash
# Simple benchmark
time curl -X POST $API_URL/reframe \
  -H "Content-Type: application/json" \
  -d '{"action":"reframe","user_id":"test","input":"test","tone":"gentle"}'
```

## Hackathon Submission Prep

Once everything works:

1. **Create architecture diagram**
   - Use Draw.io or Excalidraw
   - Save as `docs/architecture.png`
   - Include in README

2. **Record demo video**
   - See `docs/HACKATHON_CHECKLIST.md`
   - 3 minutes maximum
   - Show live demo + explain architecture

3. **Write Devpost description**
   - What it does
   - How it works
   - AWS services used
   - Value proposition

4. **Final checks**
   - [ ] GitHub repo is public
   - [ ] README is complete
   - [ ] Demo video uploaded
   - [ ] Live URL works
   - [ ] All tests pass

## Teardown

When done:

```bash
cd infra
./teardown.sh
```

⚠️ **Warning:** This deletes everything including data!

## Support Resources

- **AWS Bedrock Docs:** https://docs.aws.amazon.com/bedrock/
- **SAM CLI Docs:** https://docs.aws.amazon.com/serverless-application-model/
- **Hackathon Rules:** https://aws-agent-hackathon.devpost.com/rules
- **Project Docs:** See `docs/` folder

## Quick Commands Reference

```bash
# Deploy
cd infra && ./deploy.sh

# Test API
curl -X POST $API_URL/reframe -H "Content-Type: application/json" \
  -d '{"action":"reframe","user_id":"test","input":"test thought","tone":"gentle"}'

# View logs
aws logs tail /aws/lambda/CognitiveReframer-Main --follow

# Check costs
aws ce get-cost-and-usage --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY --metrics BlendedCost

# Update frontend
cd frontend && aws s3 sync . s3://<bucket-name>/

# Teardown
cd infra && ./teardown.sh
```

---

**Ready to go? Run `cd infra && ./deploy.sh` to start! 🚀**

