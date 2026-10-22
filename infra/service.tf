resource "aws_ecs_service" "app" {
  count                             = var.enable_app ? 1 : 0
  name                              = "rag-supply-service"
  cluster                           = aws_ecs_cluster.main.id
  task_definition                   = aws_ecs_task_definition.app.arn
  desired_count                     = 1
  launch_type                       = "FARGATE"
  health_check_grace_period_seconds = 300

  network_configuration {
    subnets          = module.network.public_subnet_ids
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app[0].arn
    container_name   = "app"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}
