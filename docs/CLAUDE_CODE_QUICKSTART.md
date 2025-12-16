# Claude Code Quick Start Guide

## 🚀 Getting Started with Claude Code

Claude Code is an AI-powered coding assistant that can help you with your quantitative finance project. This guide will help you set it up and start using it effectively.

## Prerequisites

✅ **Completed Setup:**
- AWS CLI installed
- AWS SSO profile configured (`bedrock-code-ai`)
- Claude Code environment variables configured

## Step 1: Login to AWS SSO

Before using Claude Code, you need to authenticate with AWS:

```bash
aws sso login --profile bedrock-code-ai
```

This will open a browser window for authentication. The session typically lasts 8-12 hours.

## Step 2: Load Environment Variables

Load the Claude Code configuration:

```bash
source config/claude_code_bedrock.env
```

Or add to your `~/.zshrc` or `~/.bashrc` for automatic loading:

```bash
echo "source $(pwd)/config/claude_code_bedrock.env" >> ~/.zshrc
```

## Step 3: Verify Setup

Run the verification script:

```bash
config/verify_claude_code_setup.sh
```

You should see:
- ✅ AWS CLI installed
- ✅ AWS SSO profile found
- ✅ AWS credentials valid
- ✅ Bedrock access verified
- ✅ Environment variables set

## Step 4: Start Using Claude Code

### In Cursor/VS Code

Claude Code is integrated into Cursor. Simply:
1. Open any file in your project
2. Use `Cmd+K` (Mac) or `Ctrl+K` (Windows/Linux) to open Claude Code
3. Ask questions or request code changes

### Example Prompts

**Market Data Analysis:**
```
"Analyze the AAPL data from test_openbb.py and add a Bollinger Bands calculation"
```

**Options Pricing:**
```
"Extend test_pyql.py to calculate Greeks for a European call option"
```

**Portfolio Analysis:**
```
"Create a portfolio optimization script using GS Quant concepts"
```

**Code Explanation:**
```
"Explain how the Black-Scholes model is implemented in test_vollib.py"
```

## Step 5: Working with Your Project

### Project Structure

Claude Code understands your project structure:
- `scripts/` - Your test and example scripts
- `docs/` - Documentation
- `config/` - Configuration files

### Best Practices

1. **Be Specific**: Include file paths and context in your requests
   ```
   "In scripts/test_openbb.py, add a function to calculate RSI"
   ```

2. **Reference Concepts**: Mention finance theory when relevant
   ```
   "Implement a mean-reversion strategy based on Principles of Corporate Finance Chapter 8"
   ```

3. **Iterate**: Build on previous conversations
   ```
   "Extend the previous portfolio optimization to include risk constraints"
   ```

4. **Test**: Always test generated code
   ```bash
   source .venv311/bin/activate
   python scripts/your_script.py
   ```

## Troubleshooting

### AWS SSO Session Expired

If you see authentication errors:
```bash
aws sso login --profile bedrock-code-ai
```

### Environment Variables Not Set

Check if variables are loaded:
```bash
echo $CLAUDE_CODE_USE_BEDROCK
echo $AWS_REGION
```

If empty, reload:
```bash
source config/claude_code_bedrock.env
```

### Bedrock Access Denied

Verify your AWS profile has Bedrock permissions:
```bash
aws bedrock list-foundation-models --profile bedrock-code-ai --region eu-west-1
```

## Next Steps

1. ✅ Complete AWS SSO login
2. ✅ Load environment variables
3. ✅ Verify setup
4. 🚀 Start coding with Claude Code!

## Resources

- [Claude Code Documentation](https://code.claude.com/docs)
- [Amazon Bedrock Setup](docs/CLAUDE_CODE_BEDROCK_SETUP.md)
- [GS Quant Explanation](docs/gs_quant_explanation.md)

