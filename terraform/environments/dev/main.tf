variable "aws_region" { default = "us-east-1" }
variable "aws_account_id" { type = string }
variable "ecr_image_uri" { type = string }
variable "ssm_secret_key_arn" { type = string }

locals {
  project_name = "policybot-dev"
  azs          = ["${var.aws_region}a"]
}

module "networking" {
  source               = "../../modules/networking"
  project_name         = local.project_name
  vpc_cidr             = "10.1.0.0/16"
  availability_zones   = local.azs
  public_subnet_cidrs  = ["10.1.1.0/24"]
  private_subnet_cidrs = ["10.1.11.0/24"]
  single_nat_gateway   = true
}

module "security" {
  source       = "../../modules/security"
  project_name = local.project_name
  vpc_id       = module.networking.vpc_id
}

module "ecr" {
  source          = "../../modules/ecr"
  repository_name = "policybot"
}

module "alb" {
  source            = "../../modules/alb"
  project_name      = local.project_name
  vpc_id            = module.networking.vpc_id
  public_subnet_ids = module.networking.public_subnet_ids
  alb_sg_id         = module.security.alb_sg_id
}

module "efs" {
  source             = "../../modules/efs"
  project_name       = local.project_name
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
  ecs_sg_id          = module.security.ecs_sg_id
}

module "ecs" {
  source               = "../../modules/ecs"
  project_name         = local.project_name
  aws_region           = var.aws_region
  aws_account_id       = var.aws_account_id
  ecr_image_uri        = var.ecr_image_uri
  private_subnet_ids   = module.networking.private_subnet_ids
  ecs_sg_id            = module.security.ecs_sg_id
  target_group_arn     = module.alb.target_group_arn
  efs_id               = module.efs.efs_id
  efs_access_point_id  = module.efs.access_point_id
  ssm_secret_key_arn   = var.ssm_secret_key_arn
  task_cpu             = 1024
  task_memory          = 4096
  desired_count        = 1
  min_capacity         = 1
  max_capacity         = 3
}

output "alb_dns_name" { value = module.alb.alb_dns_name }
output "efs_id" { value = module.efs.efs_id }
