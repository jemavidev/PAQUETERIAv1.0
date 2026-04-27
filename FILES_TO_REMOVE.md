# 🗑️ Files to Remove After Migration

## ✅ Safe to Remove (Old Deploy System)

Once you've tested the new system and everything works, you can remove these files:

### Old Deploy System
```bash
# Old deploy script (replaced by .deploy/deploy.sh)
deploy.sh

# Old deploy folder (replaced by .deploy-universal → .deploy)
.deploy/
├── config/
│   ├── deploy.conf
│   ├── localhost.conf
│   ├── papyrus.conf
│   └── staging.conf
├── lib/
│   ├── colors.sh  (replaced with modular version)
│   └── git.sh     (replaced with modular version)
├── hooks/         (KEEP if you have custom hooks)
│   ├── pre-deploy-papyrus.sh
│   └── post-deploy-papyrus.sh
└── docs/          (old documentation)
```

### Backup Files
```bash
# After 1 week of successful use
.deploy-backup-*
deploy.sh.backup
```

### History Files
```bash
# Old deploy history (optional, keep for audit)
.deploy-history
.deploy-current
```

## ⚠️ KEEP These Files

### Essential Project Files
```bash
# Environment files
.env
.env.staging
.env.production

# Docker Compose files
docker-compose.dev.yml
docker-compose.staging.yml
docker-compose.prod.yml

# New deploy system
.deploy/                    # New universal system
.deploy-config.yml          # Your configuration

# SSH keys
.ssh_keys/
```

### Custom Hooks (If You Have Them)
```bash
# Move these to new location if needed
.deploy/hooks/pre-deploy-papyrus.sh
.deploy/hooks/post-deploy-papyrus.sh
```

## 📝 Removal Commands

### Step 1: Backup First
```bash
# Create backup before removing
tar -czf old-deploy-backup-$(date +%Y%m%d).tar.gz \
  deploy.sh \
  .deploy/ \
  .deploy-history \
  .deploy-current

# Move backup to safe location
mv old-deploy-backup-*.tar.gz ~/backups/
```

### Step 2: Remove Old System
```bash
# Remove old deploy script
rm deploy.sh

# Remove old deploy folder
rm -rf .deploy/

# Remove history files (optional)
rm .deploy-history
rm .deploy-current
```

### Step 3: Install New System
```bash
# Copy universal system
cp -r .deploy-universal .deploy

# Make executable
chmod +x .deploy/deploy.sh

# Your config is already created
ls -la .deploy-config.yml
```

### Step 4: Clean Up
```bash
# After 1 week of successful use
rm -rf .deploy-backup-*
rm deploy.sh.backup
rm ~/backups/old-deploy-backup-*.tar.gz
```

## 🔍 Verification Before Removal

Before removing old files, verify:

```bash
# 1. New system works
./.deploy/deploy.sh status localhost
./.deploy/deploy.sh status staging
./.deploy/deploy.sh status production

# 2. All environments accessible
./.deploy/deploy.sh health localhost
./.deploy/deploy.sh health staging
./.deploy/deploy.sh health production

# 3. Deploy works
./.deploy/deploy.sh deploy localhost

# 4. Rollback works
./.deploy/deploy.sh rollback localhost
```

## 📊 File Size Comparison

### Old System
```
deploy.sh                    ~40 KB (1,100 lines)
.deploy/config/*.conf        ~20 KB
.deploy/lib/*.sh             ~10 KB
Total:                       ~70 KB
```

### New System
```
.deploy/deploy.sh            ~15 KB (300 lines)
.deploy/lib/*.sh             ~30 KB (8 modules)
.deploy-config.yml           ~5 KB
Total:                       ~50 KB
```

**Savings:** ~20 KB + better organization

## 🎯 What Stays, What Goes

### ✅ KEEP
- `.deploy/` (new universal system)
- `.deploy-config.yml` (your configuration)
- `.env*` files
- `docker-compose*.yml` files
- `.ssh_keys/` (if you have them)
- Custom hooks (move to `.deploy/hooks/`)

### ❌ REMOVE
- `deploy.sh` (old script)
- Old `.deploy/` folder (after backup)
- `.deploy-history` (optional)
- `.deploy-current` (optional)
- Backup files (after 1 week)

### 🤔 OPTIONAL
- `.deploy-history` - Keep for audit trail
- `.deploy-current` - Not needed anymore
- Old backups - Keep for 1 week, then remove

## 🚨 Important Notes

1. **Always backup before removing**
2. **Test new system thoroughly first**
3. **Keep backups for at least 1 week**
4. **Document any custom modifications**
5. **Update team documentation**

## ✅ Checklist

Before removing old files:

- [ ] New system tested on localhost
- [ ] New system tested on staging
- [ ] New system tested on production
- [ ] All team members trained
- [ ] Backup created
- [ ] CI/CD updated (if applicable)
- [ ] Documentation updated
- [ ] 1 week of successful use

After checklist complete:
```bash
# Safe to remove old system
rm -rf deploy.sh .deploy-backup-* .deploy-history .deploy-current
```

## 🎉 Result

After cleanup:
```
your-project/
├── .deploy/              # ✅ New universal system
├── .deploy-config.yml    # ✅ Your configuration
├── .env*                 # ✅ Environment files
├── docker-compose*.yml   # ✅ Docker configs
└── [your code]           # ✅ Your application
```

Clean, organized, and ready to scale! 🚀
