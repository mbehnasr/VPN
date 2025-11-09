terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }

  # Configure a remote backend (S3 + DynamoDB) before production use.
  # backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-noble-24.04-amd64-server-*"]
  }
}

resource "aws_security_group" "vpn_bot" {
  name        = "vpn-bot-sg"
  description = "Allow SSH, HTTP, HTTPS for VPN Telegram bot"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, { Name = "${var.project}-sg" })
}

resource "aws_instance" "vpn_bot" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.vpn_bot.id]
  key_name                    = var.key_name
  associate_public_ip_address = true
  iam_instance_profile        = var.iam_instance_profile

  user_data = file("${path.module}/../scripts/cloud-init.sh")

  tags = merge(var.tags, { Name = "${var.project}-ec2" })
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.vpn_bot.id
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.vpn_bot.public_ip
}

