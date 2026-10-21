variable "enable_app" {
  description = "true = build the load balancer and the Fargate service (costs money). false = do not build them"
  type        = bool
  default     = false
}

variable "image_tag" {
  description = "Tag of the Docker image the task runs (a commit ID, or latest)"
  type        = string
  default     = "fd4e0464203b6e08ec8e5dc95fbce51075bae64d"
}
