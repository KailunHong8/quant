# Claude Code + Amazon Bedrock Setup Guide

## Overview

This guide sets up Claude Code to use Amazon Bedrock with your AWS SSO profile (`bedrock-code-ai`) in the `eu-west-1` region.

**Reference Documentation:**
- [Claude Code on Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock#2-configure-aws-credentials)

## Prerequisites

✅ AWS CLI installed (`aws --version`)
✅ AWS SSO profile configured (`bedrock-code-ai`)
✅ Access to Bedrock in `eu-west-1` region

## Setup Steps

### Step 1: AWS SSO Profile Configuration

The profile has been added to your `~/.aws/config`:

```ini
[profile bedrock-code-ai]
sso_start_url = https://hfsso.awsapps.com/start
sso_region = eu-west-1
sso_account_id = 951719175506
sso_role_name = bedrock-user
region = eu-west-1
```

### Step 2: AWS SSO Login

**First-time login:**
```bash
aws sso login --profile bedrock-code-ai
```

This will:
- Open your browser for SSO authentication
- Cache credentials for future use
- Credentials typically last 8-12 hours

**Subsequent logins:**
```bash
# If credentials expired, login again
aws sso login --profile bedrock-code-ai
```

### Step 3: Verify AWS Access

```bash
export AWS_PROFILE=bedrock-code-ai
export AWS_REGION=eu-west-1
aws sts get-caller-identity
```

You should see your AWS account and user information.

### Step 4: Verify Bedrock Access

```bash
aws bedrock list-foundation-models \
  --region eu-west-1 \
  --query 'modelSummaries[?contains(modelId, `claude`)].modelId' \
  --output text
```

This should list available Claude models in your region.

### Step 5: Configure Claude Code Environment Variables

**Option A: Source the configuration file (Recommended)**

```bash
source /Users/kailun.hong/Documents/Personal/quant/claude_code_bedrock.env
```

**Option B: Add to your shell profile (~/.zshrc or ~/.bash_profile)**

```bash
# Add these lines to ~/.zshrc (or ~/.bash_profile)
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=eu-west-1
export AWS_PROFILE=bedrock-code-ai
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096
export MAX_THINKING_TOKENS=1024
```

Then reload:
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

**Option C: Export manually (temporary, current session only)**

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=eu-west-1
export AWS_PROFILE=bedrock-code-ai
export CLAUDE_CODE_MAX_OUTPUT_TOKENS=4096
export MAX_THINKING_TOKENS=1024
```

## Configuration Details

### Required Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `CLAUDE_CODE_USE_BEDROCK` | `1` | Enables Bedrock integration |
| `AWS_REGION` | `eu-west-1` | **Required** - Claude Code doesn't read from `.aws/config` |
| `AWS_PROFILE` | `bedrock-code-ai` | Your SSO profile name |

### Recommended Token Settings

| Variable | Value | Why |
|----------|-------|-----|
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `4096` | Bedrock's minimum for burndown throttling |
| `MAX_THINKING_TOKENS` | `1024` | Balance between thinking and tool use |

### Optional Configuration

```bash
# Custom model selection (inference profile IDs)
export ANTHROPIC_MODEL='global.anthropic.claude-sonnet-4-5-20250929-v1:0'
export ANTHROPIC_SMALL_FAST_MODEL='us.anthropic.claude-haiku-4-5-20251001-v1:0'

# Override region for Haiku model
export ANTHROPIC_SMALL_FAST_MODEL_AWS_REGION=eu-west-1

# Disable prompt caching (if needed)
export DISABLE_PROMPT_CACHING=1
```

## Default Models

Claude Code uses these default models with Bedrock:

| Model Type | Default Model ID |
|------------|------------------|
| Primary | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| Small/Fast | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |

**Note:** Model availability may vary by region. Check with:
```bash
aws bedrock list-inference-profiles --region eu-west-1
```

## Verification Checklist

- [ ] AWS SSO profile configured in `~/.aws/config`
- [ ] SSO login successful: `aws sso login --profile bedrock-code-ai`
- [ ] AWS identity verified: `aws sts get-caller-identity`
- [ ] Bedrock models accessible in `eu-west-1`
- [ ] Environment variables set (check with `env | grep CLAUDE_CODE`)
- [ ] Claude Code recognizes Bedrock (check Claude Code settings/logs)

## Troubleshooting

### "Config profile (bedrock-code-ai) could not be found"
- Verify profile exists: `cat ~/.aws/config | grep -A 5 bedrock-code-ai`
- Check profile name matches exactly

### "Credentials expired"
- Run: `aws sso login --profile bedrock-code-ai`
- SSO credentials typically expire after 8-12 hours

### "Region not supported"
- Verify models available: `aws bedrock list-foundation-models --region eu-west-1`
- Check if you need to request model access in AWS Bedrock console

### "on-demand throughput isn't supported"
- Use inference profile IDs instead of direct model IDs
- Example: `export ANTHROPIC_MODEL='global.anthropic.claude-sonnet-4-5-20250929-v1:0'`

### Claude Code not using Bedrock
- Verify `CLAUDE_CODE_USE_BEDROCK=1` is set
- Check `AWS_REGION` is set (Claude Code doesn't read from `.aws/config`)
- Restart Claude Code after setting environment variables

## Advanced: Automatic Credential Refresh

For automatic SSO credential refresh, add to Claude Code settings file:

```json
{
  "awsAuthRefresh": "aws sso login --profile bedrock-code-ai",
  "env": {
    "AWS_PROFILE": "bedrock-code-ai",
    "AWS_REGION": "eu-west-1"
  }
}
```

This automatically refreshes credentials when they expire.

## IAM Permissions Required

Your AWS account needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:ListInferenceProfiles"
      ],
      "Resource": [
        "arn:aws:bedrock:*:*:inference-profile/*",
        "arn:aws:bedrock:*:*:application-inference-profile/*",
        "arn:aws:bedrock:*:*:foundation-model/*"
      ]
    }
  ]
}
```

## Quick Start Commands

```bash
# 1. Login to AWS SSO
aws sso login --profile bedrock-code-ai

# 2. Load Claude Code configuration
source /Users/kailun.hong/Documents/Personal/quant/claude_code_bedrock.env

# 3. Verify setup
aws sts get-caller-identity
aws bedrock list-foundation-models --region eu-west-1 --query 'modelSummaries[?contains(modelId, `claude`)].modelId' --output text | head -3

# 4. Start using Claude Code with Bedrock!
```

## Notes

- **Region**: Must be `eu-west-1` to match your SSO profile
- **Credentials**: SSO credentials expire; re-login when needed
- **VS Code**: If using VS Code extension, configure environment variables in extension settings, not shell
- **`/login` and `/logout`**: Disabled when using Bedrock (authentication via AWS)

