#!/bin/bash
# Setup AWS SSO Profile for Claude Code + Bedrock

echo "=========================================="
echo "AWS SSO Profile Setup for Claude Code"
echo "=========================================="
echo ""

AWS_CONFIG_FILE="${HOME}/.aws/config"
AWS_CREDENTIALS_FILE="${HOME}/.aws/credentials"

# Check if config file exists, create if not
if [ ! -f "$AWS_CONFIG_FILE" ]; then
    mkdir -p "${HOME}/.aws"
    touch "$AWS_CONFIG_FILE"
    echo "✓ Created AWS config file: $AWS_CONFIG_FILE"
fi

# Check if profile already exists
if grep -q "\[profile bedrock-code-ai\]" "$AWS_CONFIG_FILE"; then
    echo "⚠ Profile 'bedrock-code-ai' already exists in $AWS_CONFIG_FILE"
    echo "   Current configuration:"
    grep -A 5 "\[profile bedrock-code-ai\]" "$AWS_CONFIG_FILE"
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping profile update."
        exit 0
    fi
    # Remove existing profile
    sed -i.bak '/\[profile bedrock-code-ai\]/,/^$/d' "$AWS_CONFIG_FILE"
fi

# Add the profile
echo "Adding profile to $AWS_CONFIG_FILE..."
cat >> "$AWS_CONFIG_FILE" << 'EOF'

[profile bedrock-code-ai]
sso_start_url = https://hfsso.awsapps.com/start
sso_region = eu-west-1
sso_account_id = 951719175506
sso_role_name = bedrock-user
region = eu-west-1
EOF

echo "✓ Profile 'bedrock-code-ai' added to AWS config"
echo ""

# Step 2: SSO Login
echo "Step 2: AWS SSO Login"
echo "=========================================="
echo ""
echo "Now you need to login with SSO. Run:"
echo ""
echo "  aws sso login --profile bedrock-code-ai"
echo ""
echo "This will open a browser for authentication."
echo ""

# Step 3: Verify
echo "Step 3: Verify Configuration"
echo "=========================================="
echo ""
echo "After SSO login, verify with:"
echo ""
echo "  export AWS_PROFILE=bedrock-code-ai"
echo "  export AWS_REGION=eu-west-1"
echo "  aws sts get-caller-identity"
echo ""
echo "Then test Bedrock access:"
echo ""
echo "  aws bedrock list-foundation-models --region eu-west-1 --query 'modelSummaries[?contains(modelId, \`claude\`)].modelId' --output text"
echo ""

