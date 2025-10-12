#!/bin/bash

##
## Cognitive Reframer - Deployment Script
## Automates SAM build, deploy, and frontend upload
##

set -e  # Exit on error

echo "🚀 Starting Cognitive Reframer deployment..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="${STACK_NAME:-cognitive-reframer}"
AWS_REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"

echo -e "${BLUE}Configuration:${NC}"
echo "  Stack Name: $STACK_NAME"
echo "  Region: $AWS_REGION"
echo "  Profile: $PROFILE"
echo ""

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install it first.${NC}"
    exit 1
fi

if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ AWS SAM CLI not found. Please install it first.${NC}"
    echo "Install with: pip install aws-sam-cli"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Check Bedrock access
echo -e "${BLUE}Checking Bedrock model access...${NC}"
BEDROCK_CHECK=$(aws bedrock list-foundation-models --region $AWS_REGION --profile $PROFILE 2>&1 || echo "error")
if [[ "$BEDROCK_CHECK" == *"error"* ]]; then
    echo -e "${YELLOW}⚠️  Warning: Cannot verify Bedrock access. Make sure you have:${NC}"
    echo "   1. Requested model access in Bedrock console"
    echo "   2. IAM permissions for bedrock:InvokeModel"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Bedrock access verified${NC}"
fi
echo ""

# Build SAM application
echo -e "${BLUE}Building SAM application...${NC}"
cd "$(dirname "$0")"
sam build --use-container

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ SAM build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Build completed${NC}"
echo ""

# Deploy SAM application
echo -e "${BLUE}Deploying SAM application...${NC}"

if [ -f samconfig.toml ]; then
    echo "Using existing samconfig.toml"
    sam deploy --profile $PROFILE
else
    echo "Running guided deployment (first time)"
    sam deploy \
        --guided \
        --stack-name $STACK_NAME \
        --region $AWS_REGION \
        --capabilities CAPABILITY_IAM \
        --profile $PROFILE
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ SAM deployment failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend deployed${NC}"
echo ""

# Get outputs
echo -e "${BLUE}Retrieving stack outputs...${NC}"

API_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --profile $PROFILE \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --profile $PROFILE \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucket`].OutputValue' \
    --output text)

FRONTEND_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --profile $PROFILE \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendUrl`].OutputValue' \
    --output text)

echo "  API URL: $API_URL"
echo "  Frontend Bucket: $FRONTEND_BUCKET"
echo "  Frontend URL: $FRONTEND_URL"
echo ""

# Update frontend with API URL
echo -e "${BLUE}Updating frontend configuration...${NC}"
cd ../frontend

# Create a temporary file with updated API endpoint
cp app.js app.js.tmp
sed "s|API_ENDPOINT_PLACEHOLDER|$API_URL|g" app.js.tmp > app.js.configured
rm app.js.tmp

echo -e "${GREEN}✓ Frontend configured${NC}"
echo ""

# Upload frontend to S3
echo -e "${BLUE}Uploading frontend to S3...${NC}"

aws s3 sync . s3://$FRONTEND_BUCKET/ \
    --exclude "app.js" \
    --exclude "*.tmp" \
    --exclude "*.configured" \
    --profile $PROFILE \
    --region $AWS_REGION

# Upload the configured app.js
aws s3 cp app.js.configured s3://$FRONTEND_BUCKET/app.js \
    --profile $PROFILE \
    --region $AWS_REGION

# Clean up temporary file
rm app.js.configured

# Set proper content types
aws s3 cp s3://$FRONTEND_BUCKET/index.html s3://$FRONTEND_BUCKET/index.html \
    --content-type "text/html" \
    --metadata-directive REPLACE \
    --profile $PROFILE \
    --region $AWS_REGION

aws s3 cp s3://$FRONTEND_BUCKET/styles.css s3://$FRONTEND_BUCKET/styles.css \
    --content-type "text/css" \
    --metadata-directive REPLACE \
    --profile $PROFILE \
    --region $AWS_REGION

aws s3 cp s3://$FRONTEND_BUCKET/app.js s3://$FRONTEND_BUCKET/app.js \
    --content-type "application/javascript" \
    --metadata-directive REPLACE \
    --profile $PROFILE \
    --region $AWS_REGION

echo -e "${GREEN}✓ Frontend deployed${NC}"
echo ""

# Test API endpoint
echo -e "${BLUE}Testing API endpoint...${NC}"
TEST_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"action":"get_user","user_id":"test"}' \
    $API_URL/user)

if [ "$TEST_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${YELLOW}⚠️  API returned status code: $TEST_RESPONSE${NC}"
fi
echo ""

# Summary
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Access your application:${NC}"
echo ""
echo -e "  Frontend URL:"
echo -e "  ${GREEN}$FRONTEND_URL${NC}"
echo ""
echo -e "  API Endpoint:"
echo -e "  ${GREEN}$API_URL${NC}"
echo ""
echo -e "${BLUE}📊 Next steps:${NC}"
echo "  1. Test the frontend in your browser"
echo "  2. Check CloudWatch logs: aws logs tail /aws/lambda/CognitiveReframer-Main --follow"
echo "  3. Monitor costs: aws ce get-cost-and-usage --time-period Start=2025-01-01,End=2025-01-31"
echo ""
echo -e "${YELLOW}💡 Tip: Bookmark the frontend URL and test with a sample thought!${NC}"
echo ""

