#!/bin/bash
set -e

DOCKER_HOST="srv01-docker01-dockeradm"
PROJECT_DIR="/home/pascal/Lernsystem"
REMOTE_DIR="/opt/docker/apps/lsx"

echo "=== LSX Deploy ==="

# 1. Build frontend locally
echo "Building frontend..."
cd "$PROJECT_DIR/frontend" && npm run build
cd "$PROJECT_DIR"

# 2. Sync code to Docker host
echo "Syncing to $DOCKER_HOST..."
rsync -avz --delete \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='.superpowers' \
  --exclude='.worktrees' \
  "$PROJECT_DIR/" "$DOCKER_HOST:$REMOTE_DIR/"

# 3. Restart containers (rebuild only if requirements.txt changed)
echo "Restarting containers..."
ssh "$DOCKER_HOST" "cd $REMOTE_DIR/docker && docker compose up -d --build"

echo ""
echo "=== Deploy complete ==="
echo "Frontend: http://10.0.50.4"
echo "Backend:  http://10.0.51.4:8000"
ssh "$DOCKER_HOST" "docker ps --filter name=lsx --format 'table {{.Names}}\t{{.Status}}'"
