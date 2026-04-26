# Replace these values with your real AWS account details before applying
aws_account_id     = "123456789012"
ecr_image_uri      = "123456789012.dkr.ecr.us-east-1.amazonaws.com/policybot:prod-latest"
ssm_secret_key_arn = "arn:aws:ssm:us-east-1:123456789012:parameter/policybot/prod/secret_key"
certificate_arn    = ""  # Set to your ACM cert ARN to enable HTTPS
