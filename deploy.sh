#!/bin/bash


set -e

PORT="${1:-8080}"

if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "ERROR: Invalid port number: $PORT"
    echo "Usage: $0 [PORT]"
    exit 1
fi

# Check for port conflicts with RabbitMQ
if [ "$PORT" -eq 5672 ] || [ "$PORT" -eq 15672 ] || [ "$PORT" -eq 1883 ]; then
    echo "ERROR: Port $PORT conflicts with RabbitMQ services"
    echo "RabbitMQ uses ports: 5672 (AMQP), 15672 (Management UI), 1883 (MQTT)"
    echo "Please choose a different port."
    exit 1
fi

echo "=========================================="
echo "  HA Dashboard + RabbitMQ Deployment"
echo "=========================================="
echo "  Port: $PORT"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

echo "[1/6] Updating system packages..."
apt-get update -qq

if ! command -v docker &> /dev/null; then
    echo "[2/6] Installing Docker..."
    apt-get install -y ca-certificates curl gnupg
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update -qq
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    echo "Docker installed successfully"
else
    echo "[2/6] Docker already installed, skipping..."
fi

# Verify Docker is running
echo "[3/6] Verifying Docker is running..."
if ! systemctl is-active --quiet docker; then
    systemctl start docker
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "[4/6] Working directory: $SCRIPT_DIR"

if [ ! -f "config.yaml" ]; then
    echo "ERROR: config.yaml not found!"
    echo "Please create config.yaml before running this script."
    exit 1
fi

if [ ! -f "assembly.yaml" ]; then
    echo "ERROR: assembly.yaml not found!"
    echo "Please ensure assembly.yaml exists in the project directory."
    exit 1
fi

echo "[5/6] Building and starting Docker containers..."
docker compose -f assembly.yaml down 2>/dev/null || true
PORT=$PORT docker compose -f assembly.yaml build --no-cache
PORT=$PORT docker compose -f assembly.yaml up -d

echo "Waiting for RabbitMQ to be healthy..."
timeout=60
while [ $timeout -gt 0 ]; do
    if docker compose -f assembly.yaml ps rabbitmq | grep -q "healthy"; then
        echo "RabbitMQ is healthy!"
        break
    fi
    echo "Waiting for RabbitMQ... ($timeout seconds remaining)"
    sleep 5
    timeout=$((timeout - 5))
done

if [ $timeout -le 0 ]; then
    echo "WARNING: RabbitMQ health check timed out. Services may still be starting..."
    echo "You can check status with: docker compose -f assembly.yaml ps"
fi

echo "[6/6] Deployment complete!"
echo ""
echo "=========================================="
echo "  Services are running!"
echo "=========================================="
echo ""
echo "  Dashboard:"
echo "    Local:    http://localhost:$PORT"
echo "    Network:  http://$(hostname -I | awk '{print $1}'):$PORT"
echo ""
echo "  RabbitMQ Management UI:"
echo "    Local:    http://localhost:15672"
echo "    Network:  http://$(hostname -I | awk '{print $1}'):15672"
echo "    Username: admin"
echo "    Password: password"
echo ""
echo "  MQTT Broker:"
echo "    Host:     $(hostname -I | awk '{print $1}')"
echo "    Port:     1883"
echo "    Username: admin"
echo "    Password: password"
echo ""
echo "  Useful commands:"
echo "    - View logs:    docker compose -f assembly.yaml logs -f"
echo "    - Stop:         docker compose -f assembly.yaml down"
echo "    - Restart:      PORT=$PORT docker compose -f assembly.yaml restart"
echo "    - Dashboard:    docker compose -f assembly.yaml logs -f dashboard"
echo "    - RabbitMQ:     docker compose -f assembly.yaml logs -f rabbitmq"
echo ""

