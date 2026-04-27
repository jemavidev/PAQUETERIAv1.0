# 🚀 Quick Start Guide - Deploy Manager Universal

## 📦 Installation (5 minutes)

### Step 1: Copy to Your Project

```bash
# Option A: Copy from this project
cp -r .deploy-universal /path/to/your-project/.deploy

# Option B: Download from repository
cd /path/to/your-project
curl -L https://github.com/your-repo/deploy-manager/archive/main.tar.gz | tar xz
mv deploy-manager-main .deploy
```

### Step 2: Create Configuration

```bash
cd /path/to/your-project

# Create config from template
cp .deploy/templates/deploy-config.yml.example .deploy-config.yml

# Edit with your data
nano .deploy-config.yml
```

### Step 3: Configure Your Environments

Edit `.deploy-config.yml`:

```yaml
project:
  name: "your-project-name"        # ← Change this
  version: "1.0.0"

localhost:
  docker:
    compose_file: "docker-compose.yml"  # ← Your file
    services: ["app", "db"]              # ← Your services

production:
  ssh:
    host: "your-server.com"        # ← Your server
    user: "ubuntu"                 # ← Your user
  paths:
    project: "/var/www/app"        # ← Your path
```

### Step 4: Test

```bash
# Make executable
chmod +x .deploy/deploy.sh

# Test localhost
./.deploy/deploy.sh deploy localhost

# Test connection to production
./.deploy/deploy.sh status production
```

## 🎯 Common Use Cases

### Use Case 1: Simple Web App

```yaml
# .deploy-config.yml
project:
  name: "my-web-app"

localhost:
  type: "local"
  docker:
    enabled: true
    compose_file: "docker-compose.yml"
    services: ["web"]
  health_check:
    url: "http://localhost:8080"

production:
  type: "remote"
  ssh:
    host: "web.example.com"
    user: "deploy"
  paths:
    project: "/var/www/app"
  docker:
    enabled: true
    compose_file: "docker-compose.prod.yml"
```

### Use Case 2: API with Database

```yaml
project:
  name: "my-api"

localhost:
  docker:
    services: ["api", "postgres", "redis"]
  migrations:
    enabled: true
    command: "docker compose exec -T api npm run migrate"

production:
  ssh:
    host: "api.example.com"
  migrations:
    enabled: true
    auto: false  # Ask confirmation in production
  backup:
    enabled: true
    auto_before_deploy: true
```

### Use Case 3: Frontend Only

```yaml
project:
  name: "my-frontend"

localhost:
  docker:
    enabled: false  # Use npm start locally

production:
  ssh:
    host: "web.example.com"
  docker:
    enabled: true
    services: ["nginx"]
  hooks:
    pre_deploy: ".deploy/hooks/build.sh"  # npm run build
```

## 🔐 Managing Secrets

### Option 1: Environment Variables

```yaml
# .deploy-config.yml
production:
  ssh:
    host: "${PROD_HOST}"
    user: "${PROD_USER}"
```

```bash
# .env (don't commit!)
PROD_HOST=157.230.45.123
PROD_USER=ubuntu
```

### Option 2: Separate Secrets File

```yaml
# .deploy-config.yml
production:
  ssh:
    config_file: ".deploy-secrets.yml"
```

```yaml
# .deploy-secrets.yml (don't commit!)
ssh:
  host: "157.230.45.123"
  user: "ubuntu"
  key: "~/.ssh/production.pem"
```

Add to `.gitignore`:
```
.deploy-secrets.yml
.env
```

## 📝 Daily Workflow

### Development (Localhost)

```bash
# Start services
./.deploy/deploy.sh deploy localhost

# Check status
./.deploy/deploy.sh status localhost

# View logs
./.deploy/deploy.sh logs localhost
```

### Deploy to Staging

```bash
# Full deploy
./.deploy/deploy.sh deploy staging

# Just pull code
./.deploy/deploy.sh pull staging

# Health check
./.deploy/deploy.sh health staging
```

### Deploy to Production

```bash
# Full deploy with confirmation
./.deploy/deploy.sh deploy production

# Create backup first
./.deploy/deploy.sh backup production

# Then deploy
./.deploy/deploy.sh deploy production
```

## 🆘 Troubleshooting

### "Config file not found"

```bash
# Create from template
cp .deploy/templates/deploy-config.yml.example .deploy-config.yml
```

### "SSH connection failed"

```bash
# Test SSH manually
ssh user@server

# Check key permissions
chmod 600 ~/.ssh/id_rsa

# Verify host in config
cat .deploy-config.yml | grep host
```

### "Docker not found"

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add user to docker group
sudo usermod -aG docker $USER
```

### "Health check failed"

```bash
# Check if service is running
./.deploy/deploy.sh status production

# Check logs
./.deploy/deploy.sh logs production

# Test health URL manually
curl http://localhost:8000/health
```

## 🔄 Rollback

If deploy fails:

```bash
# List checkpoints
./.deploy/deploy.sh rollback production

# Enter checkpoint ID when prompted
```

Or automatic rollback (if enabled in config):
```yaml
global:
  rollback:
    enabled: true  # Auto-rollback on failure
```

## 🎓 Next Steps

1. ✅ Read full documentation: `.deploy/README.md`
2. ✅ See examples: `.deploy/examples/`
3. ✅ Configure CI/CD: See GitHub Actions example
4. ✅ Set up monitoring: Add health checks
5. ✅ Create hooks: Custom pre/post deploy scripts

## 💡 Tips

- Start with localhost, then staging, then production
- Always test in staging first
- Enable backups in production
- Use rollback if something goes wrong
- Keep secrets out of git
- Document your custom hooks

## 🤝 Need Help?

- Check examples: `.deploy/examples/`
- Read docs: `.deploy/README.md`
- See FAQ: `.deploy/docs/FAQ.md`

Happy deploying! 🚀
