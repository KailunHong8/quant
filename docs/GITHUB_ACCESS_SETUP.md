# GitHub Repository Access Setup

## Adding Access for KailunHongHelloFresh

There are several ways to grant access to your `KailunHong8/quant` repository for `KailunHongHelloFresh`:

### Option 1: Add as Collaborator (User Account)

If `KailunHongHelloFresh` is a **user account**, add them as a collaborator:

#### Via GitHub Web Interface:
1. Go to: https://github.com/KailunHong8/quant/settings/access
2. Click "Add people" or "Invite a collaborator"
3. Enter username: `KailunHongHelloFresh`
4. Select permission level:
   - **Read**: View and clone only
   - **Triage**: Read + manage issues/PRs
   - **Write**: Read + push commits
   - **Maintain**: Write + manage settings (except dangerous)
   - **Admin**: Full access
5. Click "Add [username] to this repository"

#### Via GitHub CLI:
```bash
# First authenticate
gh auth login

# Add collaborator with write access
gh api repos/KailunHong8/quant/collaborators/KailunHongHelloFresh \
  -X PUT \
  -f permission=push

# Or with read-only access
gh api repos/KailunHong8/quant/collaborators/KailunHongHelloFresh \
  -X PUT \
  -f permission=pull
```

### Option 2: Transfer to Organization

If `KailunHongHelloFresh` is an **organization** and you want to transfer ownership:

1. Go to: https://github.com/KailunHong8/quant/settings
2. Scroll to "Danger Zone"
3. Click "Transfer ownership"
4. Enter: `KailunHongHelloFresh`
5. Type the repository name to confirm
6. Click "I understand, transfer this repository"

**Note**: This transfers full ownership. You'll need admin access to the organization.

### Option 3: Add Organization as Collaborator

If `KailunHongHelloFresh` is an **organization** and you want to keep ownership but grant access:

1. Go to: https://github.com/KailunHong8/quant/settings/access
2. Click "Add teams" or "Invite an organization"
3. Select the organization: `KailunHongHelloFresh`
4. Choose a team within the organization (or create one)
5. Set permission level
6. Click "Add [team] to this repository"

### Option 4: Use GitHub CLI Script

I can create a script to automate this. Here's a helper script:

```bash
#!/bin/bash
# Add collaborator to repository

REPO="KailunHong8/quant"
COLLABORATOR="KailunHongHelloFresh"
PERMISSION="push"  # Options: pull, push, admin, maintain, triage

echo "Adding $COLLABORATOR to $REPO with $PERMISSION access..."

gh api repos/$REPO/collaborators/$COLLABORATOR \
  -X PUT \
  -f permission=$PERMISSION

if [ $? -eq 0 ]; then
  echo "✅ Successfully added $COLLABORATOR"
  echo "They will receive an email invitation."
else
  echo "❌ Failed to add collaborator"
  echo "Make sure:"
  echo "  1. Repository exists: https://github.com/$REPO"
  echo "  2. You have admin access"
  echo "  3. GitHub CLI is authenticated: gh auth login"
fi
```

## Verify Access

After adding access, verify:

```bash
# List collaborators
gh api repos/KailunHong8/quant/collaborators

# Check specific user
gh api repos/KailunHong8/quant/collaborators/KailunHongHelloFresh
```

## Permission Levels Explained

- **Read (pull)**: Clone, pull, view issues/PRs
- **Triage**: Read + manage issues and pull requests
- **Write (push)**: Read + push commits, create branches
- **Maintain**: Write + manage repository settings (except dangerous)
- **Admin**: Full access including deletion and transfer

## Troubleshooting

### "Repository not found"
- Make sure the repository exists: https://github.com/KailunHong8/quant
- Verify you have admin access

### "User not found"
- Check the exact username: `KailunHongHelloFresh`
- It might be an organization, not a user

### "Permission denied"
- Authenticate with GitHub CLI: `gh auth login`
- Ensure you have admin rights to the repository

## Quick Command Reference

```bash
# Authenticate GitHub CLI
gh auth login

# Add collaborator (write access)
gh api repos/KailunHong8/quant/collaborators/KailunHongHelloFresh -X PUT -f permission=push

# List all collaborators
gh api repos/KailunHong8/quant/collaborators

# Remove collaborator
gh api repos/KailunHong8/quant/collaborators/KailunHongHelloFresh -X DELETE
```

