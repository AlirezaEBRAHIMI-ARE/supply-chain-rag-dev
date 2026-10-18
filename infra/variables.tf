variable "enable_app" {
  description = "true = build the load balancer and the Fargate service (costs money). false = do not build them"
  type        = bool
  default     = false
}
