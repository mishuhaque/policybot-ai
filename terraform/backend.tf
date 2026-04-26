terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Replace {account-id} with your AWS account ID before running terraform init
    bucket         = "policybot-terraform-state-{account-id}"
    key            = "policybot/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "policybot-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region
}
