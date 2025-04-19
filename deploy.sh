#!/bin/bash

# Simple deployment script for Caption Generator API

# Make script exit on first error
set -e

# Display usage information
show_usage() {
  echo "Usage: ./deploy.sh [option]"
  echo "Options:"
  echo "  --build       Build Docker image"
  echo "  --up          Start containers"
  echo "  --down        Stop containers"
  echo "  --logs        Show logs"
  echo "  --restart     Restart containers"
  echo "  --help        Show this help message"
}

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo "Please edit .env file with your API keys before proceeding."
  exit 1
fi

# Check if data directory exists
if [ ! -d "data" ]; then
  echo "Creating data directory..."
  mkdir -p data
fi

# Process command line arguments
case "$1" in
  --build)
    echo "Building Docker image..."
    docker-compose build
    ;;
  --up)
    echo "Starting containers..."
    docker-compose up -d
    echo "API is now running at http://localhost:8000"
    echo "Documentation available at http://localhost:8000/docs"
    ;;
  --down)
    echo "Stopping containers..."
    docker-compose down
    ;;
  --logs)
    echo "Showing logs..."
    docker-compose logs -f
    ;;
  --restart)
    echo "Restarting containers..."
    docker-compose restart
    ;;
  --help)
    show_usage
    ;;
  *)
    echo "Unknown option: $1"
    show_usage
    exit 1
    ;;
esac

exit 0 