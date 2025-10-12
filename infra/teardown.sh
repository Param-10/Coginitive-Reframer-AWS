#!/bin/bash

##
## Cognitive Reframer - Teardown Script
## Safely removes all AWS resources
##

set -e

echo "🗑️  Cognitive Reframer Teardown"
echo ""

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Configuration
STACK_NAME="${STACK_NAME:-cognitive-reframer}"
AWS_REGION="${AWS_REGION:-us-east-1}"
PROFILE="${AWS_PROFILE:-default}"

echo -e "${YELLOW}⚠️  WARNING: This will delete all resources for $STACK_NAME${NC}"
echo ""
echo "This includes:"
echo "  • Lambda functions"
echo "  • DynamoDB tables (and all data)"
echo "  • S3 bucket (and all files)"
echo "  • API Gateway"
echo "  • CloudWatch logs"
echo ""

read -p "Are you sure you want to continue? (type 'yes' to confirm): " -r
echo ""

if [[ ! $REPLY == "yes" ]]; then
    echo "Teardown cancelled."
    exit 0
fi

# Get frontend bucket name
echo "Retrieving resources..."
FRONTEND_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --profile $PROFILE \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucket`].OutputValue' \
    --output text 2>/dev/null || echo "")

# Empty S3 bucket first (required before stack deletion)
if [ -n "$FRONTEND_BUCKET" ]; then
    echo "Emptying S3 bucket: $FRONTEND_BUCKET"
    aws s3 rm s3://$FRONTEND_BUCKET --recursive --profile $PROFILE --region $AWS_REGION
    echo -e "${GREEN}✓ S3 bucket emptied${NC}"
else
    echo "No S3 bucket found or stack doesn't exist"
fi
echo ""

# Delete CloudFormation stack
echo "Deleting CloudFormation stack..."
aws cloudformation delete-stack \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --profile $PROFILE

echo "Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete \
    --stack-name $STACK_NAME \
    --region $AWS_REGION \
    --profile $PROFILE

echo -e "${GREEN}✓ Stack deleted${NC}"
echo ""

# Delete CloudWatch log groups
echo "Cleaning up CloudWatch log groups..."
LOG_GROUPS=$(aws logs describe-log-groups \
    --log-group-name-prefix "/aws/lambda/CognitiveReframer" \
    --region $AWS_REGION \
    --profile $PROFILE \
    --query 'logGroups[*].logGroupName' \
    --output text)

for LOG_GROUP in $LOG_GROUPS; do
    echo "  Deleting $LOG_GROUP"
    aws logs delete-log-group \
        --log-group-name $LOG_GROUP \
        --region $AWS_REGION \
        --profile $PROFILE 2>/dev/null || true
done

echo -e "${GREEN}✓ Log groups cleaned up${NC}"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Teardown complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "All resources have been removed."
echo ""

