terraform {
    required_providers{
        aws = {
            source="hashicorp/aws"
            version="~>6.0"
        }
    }
}

provider "aws"{
    region="eu-west-3"
}

resource "aws_ecr_repository" "app" {
    name = "rag-supply-app"
    force_delete=true

    image_scanning_configuration{
      scan_on_push= true
    }
}

output "repository_url" {
    value = aws_ecr_repository.app.repository_url
}
