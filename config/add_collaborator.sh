#!/bin/bash
# Add collaborator to KailunHong8/quant repository

REPO="KailunHong8/quant"
COLLABORATOR="KailunHongHelloFresh"
PERMISSION="${1:-push}"  # Default to 'push', can override: ./add_collaborator.sh pull

echo "=========================================="
echo "Add Collaborator to GitHub Repository"
echo "=========================================="
echo ""
echo "Repository: $REPO"
echo "Collaborator: $COLLABORATOR"
echo "Permission: $PERMISSION"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "   Install: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "⚠️  GitHub CLI not authenticated"
    echo "   Run: gh auth login"
    exit 1
fi

echo "Adding collaborator..."
echo ""

# Add collaborator
gh api repos/$REPO/collaborators/$COLLABORATOR \
  -X PUT \
  -f permission=$PERMISSION

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Successfully added $COLLABORATOR to $REPO"
  echo "   Permission level: $PERMISSION"
  echo "   They will receive an email invitation."
  echo ""
  echo "To verify:"
  echo "  gh api repos/$REPO/collaborators"
else
  echo ""
  echo "❌ Failed to add collaborator"
  echo ""
  echo "Possible issues:"
  echo "  1. Repository doesn't exist: https://github.com/$REPO"
  echo "  2. You don't have admin access"
  echo "  3. Username/organization name is incorrect: $COLLABORATOR"
  echo "  4. GitHub CLI authentication expired: gh auth login"
  echo ""
  echo "Permission options:"
  echo "  pull    - Read only"
  echo "  push    - Read and write"
  echo "  admin   - Full access"
  echo "  maintain - Write + manage settings"
  echo "  triage  - Read + manage issues/PRs"
  exit 1
fi

