terraform {

    required_providers{
        aws = {
            source = "hashicorp/aws"
            version = "~>6.0"
        }
    }
}

provider "aws" {
    region = "eu-west-3"
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "state" {
  bucket = "rag-supply-tfstate-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
    bucket                   = aws_s3_bucket.state.id
    block_public_acls        = true
    block_public_policy      = true
    ignore_public_acls       = true
    restrict_public_buckets  = true
}

output "bucket_name" {
    value = aws_s3_bucket.state.id
}
