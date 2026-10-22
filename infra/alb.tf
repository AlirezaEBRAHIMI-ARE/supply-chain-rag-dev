resource "aws_lb" "app" {
  count              = var.enable_app ? 1 : 0
  name               = "rag-supply-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.network.public_subnet_ids
  idle_timeout       = 120
}

resource "aws_lb_target_group" "app" {
  count                = var.enable_app ? 1 : 0
  name                 = "rag-supply-tg"
  port                 = 8000
  protocol             = "HTTP"
  target_type          = "ip"
  vpc_id               = module.network.vpc_id
  deregistration_delay = 30

  health_check {
    path                = "/"
    matcher             = "200"
    interval            = 30
    timeout             = 10
    healthy_threshold   = 2
    unhealthy_threshold = 5
  }
}

resource "aws_lb_listener" "http" {
  count             = var.enable_app ? 1 : 0
  load_balancer_arn = aws_lb.app[0].arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app[0].arn
  }
}

output "alb_dns_name" {
  value = var.enable_app ? aws_lb.app[0].dns_name : "app is switched off (enable_app = false)"
}
