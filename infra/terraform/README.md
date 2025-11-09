# Terraform Deployment

This module provisions the baseline AWS infrastructure for the VPN Telegram bot.

## Resources

- Security group allowing SSH (restricted), HTTP, HTTPS.
- Ubuntu 24.04 EC2 instance (default `t3.micro`) with user data that installs Docker and starts the app via `docker compose`.

## Usage

```bash
cd infra/terraform
terraform init   # configure S3/DynamoDB backend before production
terraform plan \
  -var="vpc_id=vpc-1234567890abcdef0" \
  -var="subnet_id=subnet-1234567890abcdef0" \
  -var="key_name=my-key" \
  -var="allowed_ssh_cidr=203.0.113.10/32"
terraform apply ...
```

Populate `services/vpn-bot/.env` on the instance with real secrets (Telegram token, etc.). The provided `infra/scripts/cloud-init.sh` includes placeholders for pulling secrets from AWS SSM Parameter Store.

