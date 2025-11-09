variable "project" {
  description = "Project name used for tagging"
  type        = string
  default     = "vpn-telegram-bot"
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-north-1"
}

variable "vpc_id" {
  description = "VPC ID where the instance will reside"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the EC2 instance"
  type        = string
}

variable "key_name" {
  description = "Name of the SSH key pair"
  type        = string
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH to the instance"
  type        = string
  default     = "0.0.0.0/0"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "iam_instance_profile" {
  description = "Optional IAM instance profile name to attach"
  type        = string
  default     = null
}

variable "tags" {
  description = "Additional tags to apply"
  type        = map(string)
  default     = {}
}

