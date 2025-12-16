#!/bin/bash
# Verification script for Claude Code + Bedrock setup

echo "=========================================="
echo "Claude Code + Bedrock Setup Verification"
echo "=========================================="
echo ""

ERRORS=0

# Check 1: AWS CLI
echo "1. Checking AWS CLI..."
if command -v aws &> /dev/null; then
    echo "   ✓ AWS CLI installed: $(aws --version | cut -d' ' -f1)"
else
    echo "   ✗ AWS CLI not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 2: AWS Profile
echo "2. Checking AWS SSO profile..."
if grep -q "\[profile bedrock-code-ai\]" ~/.aws/config 2>/dev/null; then
    echo "   ✓ Profile 'bedrock-code-ai' found in ~/.aws/config"
    REGION=$(grep -A 5 "\[profile bedrock-code-ai\]" ~/.aws/config | grep "region" | awk '{print $3}')
    if [ "$REGION" = "eu-west-1" ]; then
        echo "   ✓ Region set to eu-west-1"
    else
        echo "   ⚠ Region is $REGION (expected eu-west-1)"
    fi
else
    echo "   ✗ Profile 'bedrock-code-ai' not found"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 3: AWS Credentials (SSO)
echo "3. Checking AWS SSO credentials..."
export AWS_PROFILE=bedrock-code-ai 2>/dev/null
export AWS_REGION=eu-west-1 2>/dev/null

if aws sts get-caller-identity &>/dev/null; then
    IDENTITY=$(aws sts get-caller-identity --output json 2>/dev/null)
    if [ $? -eq 0 ]; then
        ACCOUNT=$(echo $IDENTITY | grep -o '"Account": "[^"]*"' | cut -d'"' -f4)
        USER=$(echo $IDENTITY | grep -o '"Arn": "[^"]*"' | cut -d'"' -f4)
        echo "   ✓ AWS credentials valid"
        echo "     Account: $ACCOUNT"
        echo "     User: $(echo $USER | rev | cut -d'/' -f1 | rev)"
    else
        echo "   ⚠ Credentials may be expired. Run: aws sso login --profile bedrock-code-ai"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "   ⚠ Cannot verify credentials. Run: aws sso login --profile bedrock-code-ai"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 4: Bedrock Access
echo "4. Checking Bedrock access in eu-west-1..."
MODELS=$(aws bedrock list-foundation-models --region eu-west-1 --query 'modelSummaries[?contains(modelId, `claude`)].modelId' --output text 2>/dev/null)
if [ $? -eq 0 ] && [ ! -z "$MODELS" ]; then
    MODEL_COUNT=$(echo $MODELS | wc -w)
    echo "   ✓ Bedrock accessible. Found $MODEL_COUNT Claude model(s)"
    echo "     Sample models:"
    echo "$MODELS" | tr '\t' '\n' | head -3 | sed 's/^/       - /'
else
    echo "   ✗ Cannot access Bedrock or no Claude models found"
    echo "     This may be normal if:"
    echo "     - Bedrock not enabled in your account"
    echo "     - Model access not requested"
    echo "     - Credentials expired (run: aws sso login --profile bedrock-code-ai)"
    ERRORS=$((ERRORS + 1))
fi
echo ""

# Check 5: Environment Variables
echo "5. Checking Claude Code environment variables..."
if [ "$CLAUDE_CODE_USE_BEDROCK" = "1" ]; then
    echo "   ✓ CLAUDE_CODE_USE_BEDROCK=1"
else
    echo "   ✗ CLAUDE_CODE_USE_BEDROCK not set"
    echo "     Run: export CLAUDE_CODE_USE_BEDROCK=1"
    ERRORS=$((ERRORS + 1))
fi

if [ "$AWS_REGION" = "eu-west-1" ]; then
    echo "   ✓ AWS_REGION=eu-west-1"
else
    echo "   ✗ AWS_REGION not set to eu-west-1 (current: ${AWS_REGION:-not set})"
    echo "     Run: export AWS_REGION=eu-west-1"
    ERRORS=$((ERRORS + 1))
fi

if [ "$AWS_PROFILE" = "bedrock-code-ai" ]; then
    echo "   ✓ AWS_PROFILE=bedrock-code-ai"
else
    echo "   ⚠ AWS_PROFILE not set (current: ${AWS_PROFILE:-not set})"
    echo "     Recommended: export AWS_PROFILE=bedrock-code-ai"
fi

if [ ! -z "$CLAUDE_CODE_MAX_OUTPUT_TOKENS" ]; then
    echo "   ✓ CLAUDE_CODE_MAX_OUTPUT_TOKENS=$CLAUDE_CODE_MAX_OUTPUT_TOKENS"
else
    echo "   ⚠ CLAUDE_CODE_MAX_OUTPUT_TOKENS not set (recommended: 4096)"
fi

if [ ! -z "$MAX_THINKING_TOKENS" ]; then
    echo "   ✓ MAX_THINKING_TOKENS=$MAX_THINKING_TOKENS"
else
    echo "   ⚠ MAX_THINKING_TOKENS not set (recommended: 1024)"
fi
echo ""

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ All checks passed! Claude Code should work with Bedrock."
    echo ""
    echo "To use Claude Code with Bedrock:"
    echo "  1. Ensure environment variables are set (source claude_code_bedrock.env)"
    echo "  2. Start Claude Code"
    echo "  3. Claude Code will use Bedrock automatically"
else
    echo "⚠ Found $ERRORS issue(s). Please fix them before using Claude Code with Bedrock."
    echo ""
    echo "Quick fix:"
    echo "  source /Users/kailun.hong/Documents/Personal/quant/claude_code_bedrock.env"
    echo "  aws sso login --profile bedrock-code-ai"
fi
echo ""

