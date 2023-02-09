# Make sure to create state bucket beforehand
terraform {
  required_version = ">= 1.3"
  backend "s3" {
    bucket  = "tf-state-mlops-churn"
    key     = "mlops-churn-stg.tfstate"
    region  = "ap-south-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

# churn_events
module "source_kinesis_stream" {
  source = "./modules/kinesis"
  retention_period = 48
  shard_count = 2
  stream_name = "${var.source_stream_name}-${var.project_id}"
  tags = var.project_id
}
