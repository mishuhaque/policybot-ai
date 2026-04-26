#!/usr/bin/env bash
# Create the OIDC provider and IAM role that GitHub Actions uses to deploy.
# Usage: ./scripts/setup-github-oidc.sh <github-org-or-user> <repo-name>
# Example: ./scripts/setup-github-oidc.sh mishuhaque policybot-ai
set -euo pipefail

GITHUB_ORG="${1:?Usage: $0 <github-org-or-user> <repo-name>}"
REPO_NAME="${2:?Usage: $0 <github-org-or-user> <repo-name>}"
REGION="${AWS_REGION:-us-east-1}"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_NAME="github-actions-policybot-deploy"
OIDC_URL="https://token.actions.githubusercontent.com"
OIDC_THUMBPRINT="6938fd4d98bab03faadb97b34396831e3780aea1"

echo "Creating OIDC provider for GitHub Actions..."
aws iam create-open-id-connect-provider \
  --url "$OIDC_URL" \
  --client-id-list "sts.amazonaws.com" \
  --thumbprint-list "$OIDC_THUMBPRINT" 2>/dev/null || echo "OIDC provider already exists"

OIDC_ARN="arn:aws:iam::${ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"

echo "Creating IAM role: ${ROLE_NAME}..."
TRUST_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "${OIDC_ARN}"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:${GITHUB_ORG}/${REPO_NAME}:*"
      }
    }
  }]
}
EOF
)

aws iam create-role \
  --role-name "$ROLE_NAME" \
  --assume-role-policy-document "$TRUST_POLICY" 2>/dev/null || echo "Role already exists, updating trust policy..."

# Deploy permissions: ECR push + ECS deploy
cat > /tmp/deploy-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecs:DescribeTaskDefinition",
        "ecs:RegisterTaskDefinition",
        "ecs:UpdateService",
        "ecs:DescribeServices"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["iam:PassRole"],
      "Resource": [
        "arn:aws:iam::${ACCOUNT_ID}:role/policybot-task-execution-role",
        "arn:aws:iam::${ACCOUNT_ID}:role/policybot-task-role"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["elasticloadbalancing:DescribeLoadBalancers"],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name "policybot-deploy" \
  --policy-document file:///tmp/deploy-policy.json

echo ""
echo "Done. Add this to your GitHub repository variables:"
echo "  AWS_ACCOUNT_ID = ${ACCOUNT_ID}"
echo "  Role ARN: arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
