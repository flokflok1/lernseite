#!/bin/bash
set -e

DOCKER_HOST="srv01-docker01-dockeradm"
PROJECT_DIR="/home/pascal/Lernsystem"
REMOTE_DIR="/opt/lsx"

echo "=== LSX Deploy ==="
echo "Syncing code to $DOCKER_HOST..."

# Sync code to Docker host (protect .env.docker on remote!)
rsync -avz --delete \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='.env.docker' \
  --exclude='*.pyc' \
  --exclude='.superpowers' \
  --exclude='.worktrees' \
  --exclude='backend/logs/*' \
  --exclude='backend/uploads/*' \
  "$PROJECT_DIR/" "$DOCKER_HOST:$REMOTE_DIR/"

echo "Building and restarting containers..."

# Build images + restart containers on Docker host
ssh "$DOCKER_HOST" "cd $REMOTE_DIR/docker && docker compose build --parallel && docker compose up -d"

echo ""
echo "=== Deploy complete ==="
echo "Frontend: http://10.0.50.4"
echo "Backend:  http://10.0.51.4:8000"
ssh "$DOCKER_HOST" "docker ps --filter name=lsx --format 'table {{.Names}}\t{{.Status}}'"
