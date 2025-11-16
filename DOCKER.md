# Docker Setup for PAuth

This document explains how to use Docker and Docker Compose with PAuth for development, testing, and production environments.

## Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ ([Install Docker Compose](https://docs.docker.com/compose/install/))

## Quick Start

### Build All Services

```bash
docker-compose build
```

### Run Specific Services

```bash
# Development environment (interactive shell)
docker-compose run --rm pauth-dev

# Run tests
docker-compose run --rm pauth-test

# Start OAuth playground
docker-compose up pauth-playground

# Run Flask example
docker-compose up pauth-flask-example
```

## Available Services

### 1. Development Environment (`pauth-dev`)

Interactive development environment with all dependencies installed.

```bash
# Start interactive shell
docker-compose run --rm pauth-dev

# Run Python with PAuth available
docker-compose run --rm pauth-dev python

# Execute a specific example
docker-compose run --rm pauth-dev python -m src.examples.basic_example
```

**Features:**
- Full Poetry environment with dev dependencies
- Hot-reload with volume mounting
- Interactive shell access

### 2. Production Environment (`pauth-prod`)

Optimized production image with minimal dependencies.

```bash
# Run production container
docker-compose up pauth-prod

# Or run as daemon
docker-compose up -d pauth-prod
```

**Features:**
- Multi-stage build for smaller image size
- Non-root user for security
- Health checks enabled
- Only runtime dependencies

### 3. Testing Environment (`pauth-test`)

Automated testing with pytest and coverage reports.

```bash
# Run all tests
docker-compose run --rm pauth-test

# Run specific test file
docker-compose run --rm pauth-test poetry run pytest src/tests/test_client.py

# Run with verbose output
docker-compose run --rm pauth-test poetry run pytest -vv
```

**Features:**
- Pytest with coverage reporting
- HTML coverage reports
- All test dependencies included

### 4. OAuth Playground (`pauth-playground`)

Interactive environment for testing OAuth flows.

```bash
# Start playground
docker-compose up pauth-playground

# Access at http://localhost:5000
```

**Features:**
- Interactive OAuth testing
- Rich terminal UI
- Port forwarding for OAuth callbacks
- Persistent data storage

### 5. Flask Example (`pauth-flask-example`)

Example Flask application demonstrating PAuth integration.

```bash
# Start Flask app
docker-compose up pauth-flask-example

# Access at http://localhost:5001
```

**Features:**
- Complete Flask integration example
- Hot-reload enabled
- Debug mode active

### 6. Security Scanner (`pauth-security`)

Security analysis and reporting service.

```bash
# Run security scan
docker-compose run --rm pauth-security
```

**Features:**
- OAuth security scanning
- Report generation
- Best practices validation

### 7. Analytics Dashboard (`pauth-analytics`)

OAuth analytics and monitoring.

```bash
# Run analytics service
docker-compose run --rm pauth-analytics
```

**Features:**
- OAuth flow analytics
- Performance monitoring
- Usage statistics

## Docker Commands Reference

### Building Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build pauth-dev

# Build without cache
docker-compose build --no-cache

# Build specific stage
docker build --target development -t pauth:dev .
docker build --target production -t pauth:prod .
docker build --target testing -t pauth:test .
```

### Running Containers

```bash
# Run service interactively
docker-compose run --rm pauth-dev

# Run service in background
docker-compose up -d pauth-prod

# Run with specific command
docker-compose run --rm pauth-dev poetry run python -c "from src.client import OAuth2Client; print('Hello!')"

# View logs
docker-compose logs -f pauth-playground
```

### Managing Services

```bash
# Start all services
docker-compose up

# Start specific services
docker-compose up pauth-dev pauth-test

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart service
docker-compose restart pauth-playground
```

### Debugging

```bash
# Execute command in running container
docker-compose exec pauth-dev bash

# View container logs
docker-compose logs pauth-dev

# Follow logs in real-time
docker-compose logs -f pauth-playground

# Check container status
docker-compose ps

# Inspect container
docker inspect pauth-dev
```

## Volume Management

The setup uses named volumes for persistent data:

- `pauth-poetry-cache`: Poetry package cache
- `pauth-playground-data`: Playground session data
- `pauth-security-reports`: Security scan reports
- `pauth-analytics-data`: Analytics data
- `pauth-docs-build`: Documentation builds

### Managing Volumes

```bash
# List volumes
docker volume ls | grep pauth

# Inspect volume
docker volume inspect pauth-poetry-cache

# Remove all volumes
docker-compose down -v

# Backup volume data
docker run --rm -v pauth-playground-data:/data -v $(pwd):/backup alpine tar czf /backup/playground-backup.tar.gz -C /data .

# Restore volume data
docker run --rm -v pauth-playground-data:/data -v $(pwd):/backup alpine tar xzf /backup/playground-backup.tar.gz -C /data
```

## Environment Variables

Create a `.env` file in the project root for configuration:

```bash
# .env file example
PAUTH_ENV=development
FLASK_ENV=development
FLASK_DEBUG=1

# OAuth Provider Credentials (for examples)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/utkarsh5026/pauth.git
cd pauth

# Build development image
docker-compose build pauth-dev
```

### 2. Development Loop

```bash
# Start development shell
docker-compose run --rm pauth-dev bash

# Inside container:
poetry install
poetry run python -m src.examples.basic_example
```

### 3. Running Tests

```bash
# Run all tests
docker-compose run --rm pauth-test

# Run with coverage
docker-compose run --rm pauth-test poetry run pytest --cov=src --cov-report=html

# View coverage report (generated in htmlcov/)
```

### 4. Testing Changes

```bash
# Make code changes on host (files are mounted)

# Run tests to verify
docker-compose run --rm pauth-test

# Test in playground
docker-compose up pauth-playground
```

## Production Deployment

### Building Production Image

```bash
# Build optimized production image
docker build --target production -t pauth:latest .

# Or using docker-compose
docker-compose build pauth-prod
```

### Running Production Container

```bash
# Run with docker-compose
docker-compose up -d pauth-prod

# Or with docker directly
docker run -d --name pauth-prod pauth:latest
```

### Health Checks

The production image includes health checks:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' pauth-prod

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' pauth-prod
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   # Fix volume permissions
   docker-compose run --rm --user root pauth-dev chown -R $(id -u):$(id -g) /app
   ```

2. **Port Already in Use**
   ```bash
   # Change ports in docker-compose.yml or stop conflicting services
   docker-compose down
   lsof -i :5000  # Find process using port
   ```

3. **Out of Disk Space**
   ```bash
   # Clean up unused resources
   docker system prune -a --volumes
   ```

4. **Build Failures**
   ```bash
   # Clear build cache and rebuild
   docker-compose build --no-cache pauth-dev
   ```

5. **Poetry Lock Issues**
   ```bash
   # Update poetry.lock
   docker-compose run --rm pauth-dev poetry lock --no-update
   ```

### Debugging Tips

```bash
# Access container shell
docker-compose run --rm pauth-dev bash

# Check Python environment
docker-compose run --rm pauth-dev poetry env info

# List installed packages
docker-compose run --rm pauth-dev poetry show

# Verify imports
docker-compose run --rm pauth-dev python -c "from src.client import OAuth2Client; print('Success!')"
```

## Performance Optimization

### Build Optimization

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build

# Multi-stage builds are already configured
# See Dockerfile for optimization details
```

### Cache Management

```bash
# Prune build cache
docker builder prune

# Remove dangling images
docker image prune

# Clean up everything
docker system prune -a
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build test image
        run: docker-compose build pauth-test
      - name: Run tests
        run: docker-compose run --rm pauth-test
```

### GitLab CI Example

```yaml
test:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker-compose build pauth-test
    - docker-compose run --rm pauth-test
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [PAuth Documentation](README.md)

## Support

For issues related to Docker setup:
1. Check this documentation
2. Review Docker logs: `docker-compose logs`
3. Open an issue on GitHub
4. Contact: utkarshpriyadarshi5026@gmail.com
