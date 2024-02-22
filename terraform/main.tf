terraform {
  backend "s3" {
    bucket = "clairways-terraform-states"
    key    = "dev/connect/clwdevops-lambda-layer/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {}

module "generate_clwdevops_lambda_layer" {
  source       = "git@github.com:clairways/terraform-modules.git//lambda_layer?ref=v1.7.1"
  name         = "clwdevops-lambda-layer"
  runtime      = "python3.11"
  mount_point  = "../"
  requirements = "../requirements.txt"
  out_dir      = "../output"
}
