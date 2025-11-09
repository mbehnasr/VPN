#!/bin/bash
set -euo pipefail

apt-get update
apt-get install -y docker.io docker-compose-plugin git awscli
systemctl enable docker --now

APP_DIR="/opt/vpn"
SERVICE_DIR="${APP_DIR}/services/vpn-bot"
REPO_URL="https://github.com/mbehnasr/VPN.git"

if [ ! -d "${APP_DIR}" ]; then
  mkdir -p "${APP_DIR}"
fi

cd "${APP_DIR}"

if [ ! -d ".git" ]; then
  git clone "${REPO_URL}" .
else
  git pull --rebase
fi

# Retrieve secrets from AWS SSM Parameter Store (placeholders)
# aws ssm get-parameter --name "/vpn/telegram_token" --with-decryption --query "Parameter.Value" --output text > .env.secret

if [ ! -f "${SERVICE_DIR}/.env" ]; then
  cp "${SERVICE_DIR}/.env.example" "${SERVICE_DIR}/.env"
  # TODO: populate ${SERVICE_DIR}/.env with real secrets, e.g.
  # TELEGRAM_TOKEN=$(aws ssm get-parameter --name "/vpn/telegram_token" --with-decryption --query "Parameter.Value" --output text)
  # sed -i "s|TELEGRAM_TOKEN=.*|TELEGRAM_TOKEN=${TELEGRAM_TOKEN}|g" "${SERVICE_DIR}/.env"
fi

cd "${SERVICE_DIR}"

docker compose pull || true
docker compose up -d --build

