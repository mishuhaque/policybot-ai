# DEPLOYMENT.md

Step-by-step guide to deploy PolicyBot to AWS ECS Fargate.

---

## Prerequisites

### Tools

Install all of these before starting:

```bash
# Terraform >= 1.5.0
brew install terraform

# AWS CLI v2
brew install awscli

# Docker 20.10+
brew install --cask docker

# GitHub CLI
brew install gh
```

Verify:
```bash
terraform --version
aws --version
docker --version
gh --version
```

### AWS Account

1. Create an AWS account at https://aws.amazon.com if you don't have one
2. Create an IAM user with `AdministratorAccess` (for initial setup only)
3. Configure the CLI:
```bash
aws configure
# Enter: Access Key ID, Secret Access Key, region (us-east-1), output format (json)
```
4. Verify access:
```bash
aws sts get-caller-identity
```

---

## Step 1 — Bootstrap Terraform State Backend

This creates the S3 bucket and DynamoDB table that Terraform uses to store and lock state. **Run once.**

```bash
./scripts/bootstrap-state-backend.sh
```

It will print something like:
```
Done. Update terraform/backend.tf with:
  bucket = "policybot-terraform-state-123456789012"
  region = "us-east-1"
```

Open `terraform/backend.tf` and replace `{account-id}` with your actual account ID:
```hcl
bucket = "policybot-terraform-state-123456789012"
```

---

## Step 2 — Store JWT Secret in SSM Parameter Store

This generates a cryptographically secure secret and stores it in AWS SSM. The ECS task reads it at startup — it is never stored in code or Docker images.

```bash
./scripts/store-secret-key.sh prod
```

It will print:
```
Stored secret at: /policybot/prod/secret_key
ARN: arn:aws:ssm:us-east-1:123456789012:parameter/policybot/prod/secret_key
```

Copy the ARN. You will need it in Step 4.

For the dev environment run the same command with `dev`:
```bash
./scripts/store-secret-key.sh dev
```

---

## Step 3 — Set Up GitHub Actions OIDC

This creates an IAM role that GitHub Actions assumes via OpenID Connect — no long-lived AWS keys are stored in GitHub.

```bash
./scripts/setup-github-oidc.sh mishuhaque policybot-ai
```

It will print:
```
Done. Add this to your GitHub repository variables:
  AWS_ACCOUNT_ID = 123456789012
  Role ARN: arn:aws:iam::123456789012:role/github-actions-policybot-deploy
```

Add `AWS_ACCOUNT_ID` as a GitHub repository variable:
1. Go to your repo → **Settings** → **Variables** → **Actions**
2. Click **New repository variable**
3. Name: `AWS_ACCOUNT_ID`, Value: your account ID

---

## Step 4 — Update Terraform Variables

Open `terraform/environments/prod/terraform.tfvars` and fill in your real values:

```hcl
aws_account_id     = "123456789012"                  # your AWS account ID
ecr_image_uri      = "123456789012.dkr.ecr.us-east-1.amazonaws.com/policybot:prod-latest"
ssm_secret_key_arn = "arn:aws:ssm:us-east-1:123456789012:parameter/policybot/prod/secret_key"
certificate_arn    = ""   # leave empty for HTTP; paste ACM cert ARN here for HTTPS
```

For dev, update `terraform/environments/dev/terraform.tfvars` similarly.

---

## Step 5 — Provision AWS Infrastructure (Terraform)

```bash
cd terraform/environments/prod

terraform init
terraform plan -out=tfplan
```

Review the plan — it will create: VPC, subnets, NAT Gateways, ALB, ECS cluster, EFS, ECR, IAM roles, security groups, auto-scaling policies, and CloudWatch log group.

Apply:
```bash
terraform apply tfplan
```

This takes **10–15 minutes**. When done, note the outputs:
```
alb_dns_name       = "policybot-alb-1234567890.us-east-1.elb.amazonaws.com"
ecr_repository_url = "123456789012.dkr.ecr.us-east-1.amazonaws.com/policybot"
efs_id             = "fs-0abc1234"
```

---

## Step 6 — Upload FAISS Index to EFS

The app reads the FAISS index from EFS at `/mnt/efs`. You need to populate it before the first deployment.

**Build the index locally:**
```bash
# Using sample policies (quick test)
python src/ingest.py

# Or using your own policy documents
python src/ingest.py --input path/to/your/policy-docs/
```

**Upload to EFS** — the easiest way is a temporary EC2 instance in the same VPC:

```bash
# Launch a small EC2 in the same VPC (use the private subnet)
# SSH into it, then:
sudo apt-get install -y amazon-efs-utils
sudo mkdir /mnt/efs
sudo mount -t efs -o tls fs-0abc1234:/ /mnt/efs   # use your EFS ID
sudo mkdir -p /mnt/efs/policy_index

# Copy index files from your local machine to EC2, then to EFS
# (from your local machine)
scp -r data/policy_index/ ec2-user@{ec2-ip}:/tmp/
# (on EC2)
sudo cp -r /tmp/policy_index/* /mnt/efs/policy_index/
```

Verify the index files exist on EFS:
```bash
ls /mnt/efs/policy_index/
# Should show: index.faiss  index.pkl
```

---

## Step 7 — Build and Push Docker Image

> **First-time note:** The Docker build pre-bakes HuggingFace models into the image. This takes **20–30 minutes** on first build due to the ~1.5GB BART model download. Subsequent builds are fast (cached layers).

```bash
ECR_URI="123456789012.dkr.ecr.us-east-1.amazonaws.com/policybot"
GIT_SHA=$(git rev-parse --short HEAD)

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin "$ECR_URI"

# Build
docker build -t "${ECR_URI}:prod-${GIT_SHA}" .

# Push
docker push "${ECR_URI}:prod-${GIT_SHA}"
```

Update `terraform/environments/prod/terraform.tfvars` with the new image URI:
```hcl
ecr_image_uri = "123456789012.dkr.ecr.us-east-1.amazonaws.com/policybot:prod-abc1234"
```

Then re-apply Terraform to update the ECS task definition:
```bash
cd terraform/environments/prod
terraform apply -auto-approve
```

---

## Step 8 — Verify the Deployment

```bash
ALB_DNS="policybot-alb-1234567890.us-east-1.elb.amazonaws.com"

# Health check (should return 200)
curl http://${ALB_DNS}/

# Get a JWT token
TOKEN=$(curl -s -X POST "http://${ALB_DNS}/token" \
  -d "username=testuser" | jq -r .access_token)

# Query a policy
curl -X POST "http://${ALB_DNS}/ask" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the parental leave policy?"}'
```

Expected response:
```json
{
  "query": "What is the parental leave policy?",
  "summary": "Employees are entitled to 12 weeks parental leave.",
  "top_k": ["HR Policy: Employees are entitled to 12 weeks parental leave."]
}
```

Check ECS service is running:
```bash
aws ecs describe-services \
  --cluster policybot-cluster \
  --services policybot-service \
  --query 'services[0].{running:runningCount,desired:desiredCount,status:status}'
```

Check CloudWatch logs:
```bash
aws logs tail /ecs/policybot --follow
```

---

## Step 9 — Enable CI/CD (Ongoing Deploys)

After the first manual deploy, all future deploys happen automatically via GitHub Actions on push to `main`.

**How it works:**
1. Push code to `main`
2. GitHub Actions runs: tests → Docker build → ECR push → ECS rolling deploy → smoke test
3. ECS replaces old tasks with new ones (zero downtime, rolling update)

**Monitor a deploy:**
```bash
# Watch ECS service during rollout
aws ecs wait services-stable \
  --cluster policybot-cluster \
  --services policybot-service
```

---

## Dev Environment

For dev, use the `dev` environment which uses a single AZ and smaller compute (~$80/month):

```bash
cd terraform/environments/dev
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

Push a dev image with `dev-` prefix to trigger dev deploys from the `develop` branch.

---

## Estimated Monthly Cost

| Component | Dev | Prod |
|---|---|---|
| ECS Fargate (tasks) | ~$30 | ~$230 |
| NAT Gateway | ~$32 (1 AZ) | ~$64 (2 AZs) |
| ALB | ~$16 | ~$20 |
| EFS | ~$1 | ~$5 |
| CloudWatch Logs | ~$1 | ~$5 |
| **Total** | **~$80/mo** | **~$325/mo** |

---

## Teardown

To destroy all AWS resources (stop billing):
```bash
cd terraform/environments/prod
terraform destroy
```

> This deletes the ECS service, ALB, EFS (and the FAISS index on it), VPC, and all associated resources. The ECR images and SSM parameter are preserved — delete them manually if needed.
