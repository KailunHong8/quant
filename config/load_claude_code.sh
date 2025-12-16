#!/bin/bash
# Load Claude Code environment variables
# Run this script: source config/load_claude_code.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_FILE="$SCRIPT_DIR/claude_code_bedrock.env"

if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
    echo "✅ Claude Code environment loaded"
else
    echo "❌ Error: $ENV_FILE not found"
    return 1
fi

