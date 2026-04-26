variable "project_name" { type = string }
variable "aws_region" { type = string }
variable "aws_account_id" { type = string }
variable "ecr_image_uri" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "ecs_sg_id" { type = string }
variable "target_group_arn" { type = string }
variable "efs_id" { type = string }
variable "efs_access_point_id" { type = string }
variable "ssm_secret_key_arn" { type = string }
variable "task_cpu" { type = number }
variable "task_memory" { type = number }
variable "desired_count" { type = number }
variable "min_capacity" { type = number }
variable "max_capacity" { type = number }

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = { Name = "${var.project_name}-cluster" }
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 30
  tags              = { Name = "/ecs/${var.project_name}" }
}

# Task Execution Role — ECS agent uses this to pull images and inject secrets
resource "aws_iam_role" "task_execution" {
  name = "${var.project_name}-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "task_execution_managed" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "task_execution_ssm" {
  name = "ssm-secrets"
  role = aws_iam_role.task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["ssm:GetParameters", "ssm:GetParameter"]
      Resource = [var.ssm_secret_key_arn]
    }]
  })
}

# Task Role — the application process uses this at runtime
resource "aws_iam_role" "task" {
  name = "${var.project_name}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "task_efs" {
  name = "efs-access"
  role = aws_iam_role.task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "elasticfilesystem:ClientMount",
        "elasticfilesystem:ClientWrite",
        "elasticfilesystem:ClientRootAccess"
      ]
      Resource = ["arn:aws:elasticfilesystem:${var.aws_region}:${var.aws_account_id}:file-system/${var.efs_id}"]
    }]
  })
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.task_execution.arn
  task_role_arn            = aws_iam_role.task.arn

  volume {
    name = "policy-index"
    efs_volume_configuration {
      file_system_id          = var.efs_id
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = var.efs_access_point_id
        iam             = "ENABLED"
      }
    }
  }

  container_definitions = jsonencode([{
    name      = "${var.project_name}-app"
    image     = var.ecr_image_uri
    essential = true

    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]

    mountPoints = [{
      sourceVolume  = "policy-index"
      containerPath = "/mnt/efs"
      readOnly      = false
    }]

    environment = [
      { name = "FAISS_INDEX_PATH", value = "/mnt/efs" },
      { name = "HF_HOME", value = "/tmp/huggingface" }
    ]

    secrets = [{
      name      = "SECRET_KEY"
      valueFrom = var.ssm_secret_key_arn
    }]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecs.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/ || exit 1"]
      interval    = 30
      timeout     = 10
      retries     = 3
      startPeriod = 120
    }
  }])
}

resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_sg_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "${var.project_name}-app"
    container_port   = 8000
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200
  health_check_grace_period_seconds  = 120

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  lifecycle {
    ignore_changes = [task_definition]
  }

  depends_on = [aws_iam_role_policy_attachment.task_execution_managed]
}

# Auto-scaling
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.project_name}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "memory" {
  name               = "${var.project_name}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 80.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

output "cluster_name" { value = aws_ecs_cluster.main.name }
output "service_name" { value = aws_ecs_service.app.name }
output "task_definition_arn" { value = aws_ecs_task_definition.app.arn }
