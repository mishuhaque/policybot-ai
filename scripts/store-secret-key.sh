#!/usr/bin/env bash
# Store JWT secret key in SSM Parameter Store for a given environment.
# Usage: ./scripts/store-secret-key.sh prod
set -euo pipefail

ENV="${1:-prod}"
REGION="${AWS_REGION:-us-east-1}"
PARAM_NAME="/policybot/${ENV}/secret_key"

SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

aws ssm put-parameter \
  --name "$PARAM_NAME" \
  --value "$SECRET" \
  --type "SecureString" \
  --overwrite \
  --region "$REGION"

PARAM_ARN=$(aws ssm get-parameter \
  --name "$PARAM_NAME" \
  --region "$REGION" \
  --query "Parameter.ARN" \
  --output text)

echo "Stored secret at: ${PARAM_NAME}"
echo "ARN: ${PARAM_ARN}"
echo ""
echo "Add this ARN to terraform.tfvars as ssm_secret_key_arn"
