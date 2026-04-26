variable "project_name" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "ecs_sg_id" { type = string }

resource "aws_efs_file_system" "main" {
  encrypted = true

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = { Name = "${var.project_name}-efs" }
}

resource "aws_security_group" "efs" {
  name        = "${var.project_name}-efs-sg"
  description = "Allow NFS from ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [var.ecs_sg_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-efs-sg" }
}

resource "aws_efs_mount_target" "main" {
  count           = length(var.private_subnet_ids)
  file_system_id  = aws_efs_file_system.main.id
  subnet_id       = var.private_subnet_ids[count.index]
  security_groups = [aws_security_group.efs.id]
}

resource "aws_efs_access_point" "policy_index" {
  file_system_id = aws_efs_file_system.main.id

  posix_user {
    uid = 1000
    gid = 1000
  }

  root_directory {
    path = "/policy_index"
    creation_info {
      owner_uid   = 1000
      owner_gid   = 1000
      permissions = "755"
    }
  }

  tags = { Name = "${var.project_name}-policy-index-ap" }
}

output "efs_id" { value = aws_efs_file_system.main.id }
output "efs_arn" { value = aws_efs_file_system.main.arn }
output "access_point_id" { value = aws_efs_access_point.policy_index.id }
