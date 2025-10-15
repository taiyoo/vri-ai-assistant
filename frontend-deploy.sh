#!/bin/bash
# frontend-deploy.sh
# Quick deployment script for frontend-only changes

set -e  # Exit on any error

echo "🚀 Starting frontend-only deployment..."

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed. Please install jq first:"
    echo "  macOS: brew install jq"
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  Amazon Linux: sudo yum install jq"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the root of the bedrock-chat project"
    exit 1
fi

# Get stack outputs for environment variables
echo "🔍 Getting stack outputs..."
STACK_OUTPUTS=$(aws cloudformation describe-stacks \
    --stack-name BedrockAIAssistantStack \
    --query 'Stacks[0].Outputs' \
    --output json)

# Extract the required values
API_ENDPOINT=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="BackendApiBackendApiUrl4A0A7879") | .OutputValue')
WS_ENDPOINT=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="WebSocketWebSocketEndpointF298FA8F") | .OutputValue')
USER_POOL_ID=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="AuthUserPoolIdC0605E59") | .OutputValue')
USER_POOL_CLIENT_ID=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="AuthUserPoolClientId8216BF9A") | .OutputValue')
REGION=$(aws configure get region)

# Extract optional OAuth values (these may not exist)
COGNITO_DOMAIN=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="CognitoDomain") | .OutputValue' 2>/dev/null || echo "")
SOCIAL_PROVIDERS=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="SocialProviders") | .OutputValue' 2>/dev/null || echo "")
FRONTEND_URL=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="FrontendURL") | .OutputValue' 2>/dev/null || echo "")

if [ -z "$API_ENDPOINT" ] || [ -z "$WS_ENDPOINT" ] || [ -z "$USER_POOL_ID" ] || [ -z "$USER_POOL_CLIENT_ID" ]; then
    echo "❌ Error: Could not retrieve all required stack outputs. Make sure the stack is deployed."
    echo "Debug info:"
    echo "  API_ENDPOINT: $API_ENDPOINT"
    echo "  WS_ENDPOINT: $WS_ENDPOINT" 
    echo "  USER_POOL_ID: $USER_POOL_ID"
    echo "  USER_POOL_CLIENT_ID: $USER_POOL_CLIENT_ID"
    echo "Available outputs:"
    echo "$STACK_OUTPUTS" | jq -r '.[].OutputKey'
    exit 1
fi

echo "✅ Using production endpoints:"
echo "  API: $API_ENDPOINT"
echo "  WebSocket: $WS_ENDPOINT"
echo "  User Pool: $USER_POOL_ID"

# Build frontend with production environment variables
echo "📦 Building frontend with production environment..."
cd frontend

# Create temporary production .env file
cat > .env.production.local << EOF
VITE_APP_API_ENDPOINT=$API_ENDPOINT
VITE_APP_WS_ENDPOINT=$WS_ENDPOINT
VITE_APP_USER_POOL_ID=$USER_POOL_ID
VITE_APP_USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID
VITE_APP_REGION=$REGION
VITE_APP_USE_STREAMING=true
EOF

# Add optional OAuth variables if they exist
if [ ! -z "$COGNITO_DOMAIN" ] && [ "$COGNITO_DOMAIN" != "null" ]; then
    echo "VITE_APP_COGNITO_DOMAIN=$COGNITO_DOMAIN" >> .env.production.local
fi

if [ ! -z "$SOCIAL_PROVIDERS" ] && [ "$SOCIAL_PROVIDERS" != "null" ]; then
    echo "VITE_APP_SOCIAL_PROVIDERS=$SOCIAL_PROVIDERS" >> .env.production.local
fi

if [ ! -z "$FRONTEND_URL" ] && [ "$FRONTEND_URL" != "null" ]; then
    echo "VITE_APP_REDIRECT_SIGNIN_URL=$FRONTEND_URL" >> .env.production.local
    echo "VITE_APP_REDIRECT_SIGNOUT_URL=$FRONTEND_URL" >> .env.production.local
fi

# Set default values for custom provider (usually disabled)
echo "VITE_APP_CUSTOM_PROVIDER_ENABLED=false" >> .env.production.local
echo "VITE_APP_CUSTOM_PROVIDER_NAME=" >> .env.production.local

echo "📄 Production environment file contents:"
cat .env.production.local

npm run build

# Clean up temporary file
rm -f .env.production.local

cd ..

# Get S3 bucket name
echo "🔍 Getting S3 bucket name..."
BUCKET_NAME=$(aws cloudformation describe-stack-resources \
    --stack-name BedrockAIAssistantStack \
    --query 'StackResources[?ResourceType==`AWS::S3::Bucket`&&contains(LogicalResourceId,`FrontendAsset`)].PhysicalResourceId' \
    --output text)

if [ -z "$BUCKET_NAME" ]; then
    echo "❌ Error: Could not find frontend S3 bucket. Make sure the stack is deployed."
    exit 1
fi

echo "📤 Uploading to S3 bucket: $BUCKET_NAME"
aws s3 sync frontend/dist/ s3://$BUCKET_NAME --delete

# Get CloudFront distribution ID
echo "🔍 Getting CloudFront distribution ID..."
DISTRIBUTION_ID=$(aws cloudformation describe-stack-resources \
    --stack-name BedrockAIAssistantStack \
    --query 'StackResources[?ResourceType==`AWS::CloudFront::Distribution`].PhysicalResourceId' \
    --output text)

if [ -z "$DISTRIBUTION_ID" ]; then
    echo "❌ Error: Could not find CloudFront distribution. Make sure the stack is deployed."
    exit 1
fi

echo "🔄 Invalidating CloudFront cache: $DISTRIBUTION_ID"
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id $DISTRIBUTION_ID \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

echo "✅ Frontend deployment complete!"
echo "📊 Invalidation ID: $INVALIDATION_ID"
echo "⏱️  Changes will be live in 5-10 minutes after cache invalidation completes."

# Get the frontend URL
FRONTEND_URL=$(aws cloudformation describe-stacks \
    --stack-name BedrockAIAssistantStack \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendURL`].OutputValue' \
    --output text)

if [ ! -z "$FRONTEND_URL" ]; then
    echo "🌐 Frontend URL: $FRONTEND_URL"
fi

echo "🎉 Done!"
