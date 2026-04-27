# 📦 Migration Guide: Old Deploy System → Universal Deploy Manager

## 🎯 Overview

This guide helps you migrate from the old deploy system (`.deploy/` folder with hardcoded values) to the new Universal Deploy Manager (configuration-driven).

## 📊 What's Changing

### Old System
```
.deploy/
├── deploy.sh (1,100 lines, hardcoded "paquetex")
├── config/
│   ├── deploy.conf (hardcoded values)
│   ├── localhost.conf (hardcoded)
│   ├── papyrus.conf (hardcoded)
│   └── staging.conf (hardcoded)
└── lib/
    ├── colors.sh
    └── git.sh
```

### New System
```
.deploy/                           # Universal tool (reusable)
├── deploy.sh (modular, generic)
├── lib/ (8 modules)
└── templates/

.deploy-config.yml                 # YOUR project data
```

## 🚀 Migration Steps

### Step 1: Backup Old System

```bash
# Backup current deploy system
cp -r .deploy .deploy-backup-$(date +%Y%m%d)
cp deploy.sh deploy.sh.backup
```

### Step 2: Install New System

```bash
# The new system is already in .deploy-universal/
# Copy it to .deploy/
rm -rf .deploy
cp -r .deploy-universal .deploy

# Make executable
chmod +x .deploy/deploy.sh
```

### Step 3: Create Configuration

Your `.deploy-config.yml` is already created with your current settings!

```bash
# Review the configuration
cat .deploy-config.yml
```

### Step 4: Test Localhost

```bash
# Test with localhost first
./.deploy/deploy.sh deploy localhost
```

### Step 5: Test Staging

```bash
# Test staging
./.deploy/deploy.sh status staging
./.deploy/deploy.sh deploy staging
```

### Step 6: Test Production

```bash
# Test production (be careful!)
./.deploy/deploy.sh status production
./.deploy/deploy.sh health production
```

## 🗑️ Files to Remove

### Safe to Delete (Old System)

```bash
# Old deploy script (replaced)
rm deploy.sh.backup

# Old deploy folder (if backup works)
rm -rf .deploy-backup-*

# Old config files (data now in .deploy-config.yml)
# These are already replaced by .deploy-universal
```

### Keep These Files

```bash
# Keep these - they're still needed
.env
.env.staging
.env.production
docker-compose.dev.yml
docker-compose.staging.yml
docker-compose.prod.yml

# Keep hooks if you have them
.deploy/hooks/pre-deploy-papyrus.sh
.deploy/hooks/post-deploy-papyrus.sh
```

## 📝 Configuration Mapping

### Old: `.deploy/config/papyrus.conf`
```bash
ENV_NAME="papyrus"
SSH_HOST="papyrus"
SSH_USER="ubuntu"
PROJECT_PATH="/home/ubuntu/paqueteria"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
```

### New: `.deploy-config.yml`
```yaml
production:
  type: "remote"
  ssh:
    host: "papyrus"
    user: "ubuntu"
  paths:
    project: "/home/ubuntu/paqueteria"
  docker:
    compose_file: "docker-compose.prod.yml"
```

## 🔄 Command Changes

### Old Commands
```bash
./deploy.sh --env papyrus --deploy
./deploy.sh --env staging --restart
./deploy.sh --env localhost --logs
```

### New Commands
```bash
./.deploy/deploy.sh deploy production
./.deploy/deploy.sh restart staging
./.deploy/deploy.sh logs localhost
```

## ✅ Verification Checklist

After migration, verify:

- [ ] Localhost deploy works
- [ ] Staging deploy works
- [ ] Production status check works
- [ ] Health checks work
- [ ] Git operations work
- [ ] Docker operations work
- [ ] Backups work (if enabled)
- [ ] Migrations work (if enabled)
- [ ] Hooks work (if configured)

## 🆘 Rollback Plan

If something goes wrong:

```bash
# Restore old system
rm -rf .deploy
cp -r .deploy-backup-YYYYMMDD .deploy
cp deploy.sh.backup deploy.sh

# Use old commands
./deploy.sh --env papyrus --status
```

## 💡 Benefits of New System

### 1. Reusable
- Copy `.deploy/` to any project
- Only change `.deploy-config.yml`

### 2. Cleaner
- No hardcoded values in code
- All data in one config file

### 3. Modular
- 8 separate library files
- Easy to maintain and extend

### 4. Safer
- Automatic rollback on failure
- Better error handling
- Validation before deploy

### 5. Flexible
- Easy to add new environments
- Easy to customize per project

## 📚 Next Steps

1. ✅ Test all environments
2. ✅ Update CI/CD pipelines (if any)
3. ✅ Document custom configurations
4. ✅ Train team on new commands
5. ✅ Remove old backup files (after 1 week)

## 🤔 FAQ

### Q: Can I use both systems temporarily?
A: Yes, keep the backup and test the new system in parallel.

### Q: What if I have custom modifications?
A: Check `.deploy-backup-*/` and port your changes to the new system.

### Q: Do I need to change my Docker Compose files?
A: No, they stay the same. Only the deploy system changes.

### Q: What about my SSH keys?
A: Same keys, just referenced in `.deploy-config.yml` now.

### Q: Can I add more environments?
A: Yes! Just add a new section in `.deploy-config.yml`.

## 🎉 Success!

Once migration is complete:

```bash
# Clean up
rm -rf .deploy-backup-*
rm deploy.sh.backup

# Commit new system
git add .deploy/ .deploy-config.yml
git commit -m "Migrate to Universal Deploy Manager v3.0"
```

Happy deploying with the new system! 🚀
