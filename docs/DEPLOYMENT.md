# Deployment Guide

Complete step-by-step guide for deploying Cognitive Reframer to AWS.

## Prerequisites

### 1. AWS Account Setup

1. **Create AWS Account** (if you don't have one)
   - Go to https://aws.amazon.com/
   - Click "Create an AWS Account"
   - Follow the registration process

2. **Request Hackathon Credits**
   - Visit the Devpost hackathon page
   - Fill out the credits request form with your project description
   - Wait for approval (usually within 24-48 hours)

3. **Create IAM User**
   ```bash
   # Log in as root user first
   # Go to IAM Console > Users > Add User
   # Username: cognitive-reframer-dev
   # Access type: Programmatic access + AWS Management Console
   # Permissions: AdministratorAccess (for hackathon; restrict in production)
   # Save the Access Key ID and Secret Access Key
   ```

### 2. Local Environment Setup

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation
aws --version

# Configure AWS CLI
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key
# Default region: us-east-1
# Default output format: json

# Install AWS SAM CLI
pip install aws-sam-cli

# Verify SAM installation
sam --version

# Install Python dependencies for local testing
pip install -r backend/lambda_reframe/requirements.txt
pip install -r tests/requirements.txt
```

## Bedrock Access

### Request Model Access

1. Open [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
2. Navigate to **Model access** in the left sidebar
3. Click **Manage model access**
4. Request access to:
   - ✅ Anthropic Claude v2 (recommended)
   - ✅ Anthropic Claude Instant v1 (faster, cheaper)
   - ✅ Amazon Titan Text Express v1 (backup option)
5. Click **Save changes**
6. Wait for approval (instant for Titan, may take hours for Claude)

### Verify Access

```bash
aws bedrock list-foundation-models --region us-east-1
```

You should see a list of available models.

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

```bash
# Make deploy script executable
chmod +x infra/deploy.sh

# Run deployment
cd infra
./deploy.sh

# The script will:
# 1. Build Lambda functions
# 2. Deploy CloudFormation stack
# 3. Upload frontend to S3
# 4. Configure API endpoints
# 5. Display access URLs
```

### Option 2: Manual Deployment

#### Step 1: Build SAM Application

```bash
cd infra
sam build --use-container
```

#### Step 2: Deploy Backend

First time deployment (guided):
```bash
sam deploy --guided
```

Answer the prompts:
- Stack Name: `cognitive-reframer`
- AWS Region: `us-east-1`
- Confirm changes: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Disable rollback: `N`
- Save arguments to samconfig.toml: `Y`

Subsequent deployments:
```bash
sam deploy
```

#### Step 3: Get Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name cognitive-reframer \
  --query 'Stacks[0].Outputs' \
  --output table
```

Save the following values:
- `ApiUrl` - Your API Gateway endpoint
- `FrontendBucket` - Your S3 bucket name
- `FrontendUrl` - Your website URL

#### Step 4: Configure Frontend

```bash
cd ../frontend

# Replace API_ENDPOINT_PLACEHOLDER with your actual API URL
export API_URL="<your-api-url-from-outputs>"
sed -i '' "s|API_ENDPOINT_PLACEHOLDER|$API_URL|g" app.js
```

#### Step 5: Upload Frontend

```bash
# Get bucket name
export BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name cognitive-reframer \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucket`].OutputValue' \
  --output text)

# Upload files
aws s3 sync . s3://$BUCKET_NAME/ --acl public-read

# Set proper content types
aws s3 cp s3://$BUCKET_NAME/index.html s3://$BUCKET_NAME/index.html \
  --content-type "text/html" --metadata-directive REPLACE

aws s3 cp s3://$BUCKET_NAME/styles.css s3://$BUCKET_NAME/styles.css \
  --content-type "text/css" --metadata-directive REPLACE

aws s3 cp s3://$BUCKET_NAME/app.js s3://$BUCKET_NAME/app.js \
  --content-type "application/javascript" --metadata-directive REPLACE
```

## Testing Deployment

### Test API Endpoint

```bash
export API_URL="<your-api-url>"

# Test user endpoint
curl -X POST $API_URL/user \
  -H "Content-Type: application/json" \
  -d '{"action":"get_user","user_id":"test_user"}'

# Should return user data with 200 status
```

### Test Reframe Endpoint

```bash
curl -X POST $API_URL/reframe \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reframe",
    "user_id": "test_user",
    "input": "I am worried about the presentation",
    "tone": "gentle"
  }'

# Should return reframes with 200 status
```

### Test Frontend

Open the Frontend URL in your browser and:
1. Enter a test thought
2. Click "Generate Reframes"
3. Verify you see two reframes with action steps
4. Try saving and checking history

## Monitoring

### CloudWatch Logs

```bash
# View Lambda logs in real-time
aws logs tail /aws/lambda/CognitiveReframer-Main --follow

# View recent errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/CognitiveReframer-Main \
  --filter-pattern "ERROR"
```

### Cost Monitoring

```bash
# Set up billing alert (one-time)
aws cloudwatch put-metric-alarm \
  --alarm-name cognitive-reframer-budget \
  --alarm-description "Alert when spending exceeds $25" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 25 \
  --comparison-operator GreaterThanThreshold

# Check current costs
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## Troubleshooting

### Bedrock Access Denied

**Error:** `AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel`

**Solution:**
1. Verify model access in Bedrock console
2. Check IAM role attached to Lambda has `bedrock:InvokeModel` permission
3. Try a different model (e.g., switch from Claude to Titan)

### Lambda Timeout

**Error:** Task timed out after 30.00 seconds

**Solution:**
1. Increase Lambda timeout in `template.yaml`:
   ```yaml
   Globals:
     Function:
       Timeout: 60  # Increase from 30 to 60
   ```
2. Redeploy: `sam deploy`

### S3 Access Denied

**Error:** 403 Forbidden when accessing frontend

**Solution:**
1. Check bucket policy allows public read:
   ```bash
   aws s3api get-bucket-policy --bucket <your-bucket-name>
   ```
2. Reapply policy from `template.yaml`

### DynamoDB Throttling

**Error:** `ProvisionedThroughputExceededException`

**Solution:**
- Tables use PAY_PER_REQUEST mode by default (no throttling)
- If you changed to provisioned mode, increase capacity or switch back to on-demand

## Updating Deployment

### Update Lambda Code

```bash
cd infra
sam build
sam deploy
```

### Update Frontend Only

```bash
cd frontend
export BUCKET_NAME=<your-bucket-name>
aws s3 sync . s3://$BUCKET_NAME/
```

### Update Configuration

1. Edit `template.yaml`
2. Run `sam deploy`

## Teardown

When done with the hackathon:

```bash
# Automated teardown
cd infra
chmod +x teardown.sh
./teardown.sh

# Or manual
aws cloudformation delete-stack --stack-name cognitive-reframer
```

⚠️ **Warning:** This deletes all data including DynamoDB tables!

## Production Considerations

For production deployment beyond the hackathon:

1. **Security**
   - Add Cognito authentication
   - Use API keys or Lambda authorizers
   - Enable CloudTrail for audit logs
   - Use Secrets Manager for API keys

2. **Reliability**
   - Add CloudFront in front of S3
   - Enable X-Ray tracing
   - Set up dead letter queues for Lambda
   - Add retry logic and exponential backoff

3. **Performance**
   - Enable Lambda Provisioned Concurrency
   - Use DynamoDB DAX for caching
   - Optimize Bedrock token usage
   - Add CloudFront caching

4. **Monitoring**
   - Set up CloudWatch dashboards
   - Create comprehensive alarms
   - Use AWS Cost Explorer for budgeting
   - Add custom metrics

## Support

- AWS Documentation: https://docs.aws.amazon.com/
- Bedrock Guide: https://docs.aws.amazon.com/bedrock/
- SAM CLI: https://docs.aws.amazon.com/serverless-application-model/
- Hackathon Discord: Check Devpost for link

