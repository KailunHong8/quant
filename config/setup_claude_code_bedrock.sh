#!/bin/bash
# Claude Code + Amazon Bedrock Setup Script
# Based on: https://code.claude.com/docs/en/amazon-bedrock#2-configure-aws-credentials

echo "=========================================="
echo "Claude Code + Amazon Bedrock Setup"
echo "=========================================="
echo ""

# Step 1: Check AWS CLI
echo "Step 1: Checking AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   brew install awscli"
    exit 1
fi
echo "✓ AWS CLI found: $(aws --version)"
echo ""

# Step 2: Check AWS credentials
echo "Step 2: Checking AWS credentials..."
if ! aws configure list | grep -q "access_key.*<not set>"; then
    echo "✓ AWS credentials found"
    aws configure list | grep -E "(access_key|secret_key|region)" | head -3
else
    echo "❌ AWS credentials not configured"
    echo "   Run: aws configure"
    echo "   Or set environment variables:"
    echo "   export AWS_ACCESS_KEY_ID=your-key"
    echo "   export AWS_SECRET_ACCESS_KEY=your-secret"
    exit 1
fi
echo ""

# Step 3: Set AWS region (required for Bedrock)
echo "Step 3: Setting AWS region..."
if [ -z "$AWS_REGION" ]; then
    # Check if region is in AWS config
    REGION=$(aws configure get region 2>/dev/null)
    if [ -z "$REGION" ]; then
        echo "⚠ AWS region not set. Setting default to us-east-1"
        export AWS_REGION=us-east-1
        echo "   You can change this by running:"
        echo "   export AWS_REGION=your-preferred-region"
    else
        export AWS_REGION=$REGION
        echo "✓ Using region from AWS config: $REGION"
    fi
else
    echo "✓ Using region from environment: $AWS_REGION"
fi
echo ""

# Step 4: Verify Bedrock access
echo "Step 4: Verifying Bedrock access..."
if aws bedrock list-foundation-models --region $AWS_REGION --query 'modelSummaries[?contains(modelId, `claude`)].modelId' --output text 2>/dev/null | grep -q claude; then
    echo "✓ Bedrock access verified. Claude models available:"
    aws bedrock list-foundation-models --region $AWS_REGION --query 'modelSummaries[?contains(modelId, `claude`)].modelId' --output text 2>/dev/null | head -5
else
    echo "⚠ Could not verify Bedrock access. This might be normal if:"
    echo "   - Bedrock is not enabled in your AWS account"
    echo "   - You need to request access to Claude models"
    echo "   - Check: https://console.aws.amazon.com/bedrock/"
fi
echo ""

# Step 5: Set Claude Code environment variables
echo "Step 5: Claude Code Environment Variables"
echo "=========================================="
echo ""
echo "Add these to your shell profile (~/.zshrc or ~/.bash_profile):"
echo ""
echo "# Claude Code + Amazon Bedrock Configuration"
echo "export CLAUDE_CODE_USE_BEDROCK=1"
echo "export AWS_REGION=${AWS_REGION:-us-east-1}"
echo ""
echo "# Optional: Override region for small/fast model (Haiku)"
echo "# export ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION=us-west-2"
echo ""
echo "# Optional: Custom model configuration"
echo "# export ANTHROPIC_MODEL='global.anthropic.claude-sonnet-4-5-20250929-v1:0'"
echo "# export ANTHROPIC_SMALL_FAST_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'"
echo ""
echo "# Recommended output token settings for Bedrock"
echo "export CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096"
echo "export MAX_THINKING_TOKENS=1024"
echo ""
echo "=========================================="
echo ""
echo "To apply immediately, run:"
echo "  source ~/.zshrc  # or ~/.bash_profile"
echo ""
echo "Or export manually in current session:"
echo "  export CLAUDE_CODE_USE_BEDROCK=1"
echo "  export AWS_REGION=$AWS_REGION"
echo "  export CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096"
echo "  export MAX_THINKING_TOKENS=1024"
echo ""

