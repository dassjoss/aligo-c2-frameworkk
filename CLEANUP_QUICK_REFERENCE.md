# 🧹 Cleanup Quick Reference Card

**Full Report:** See `CLEANUP_DIAGNOSTIC_REPORT.md`

---

## ⚡ Quick Actions (Copy-Paste Commands)

### 1️⃣ Delete Obsolete Files (100% Safe)

```bash
cd /home/els4nchez/Music/aligo-c2-frameworkk

# Delete legacy TCP agents (obsolete)
rm agent/agent.py
rm agent/agent_hotspot.py

# Delete empty placeholder files
rm agent/main.py
rm server/main.py
rm interface/main.py
rm shared/README.md

# Remove empty interface directory
rmdir interface/
```

---

### 2️⃣ Consolidate Documentation

```bash
# Create structure
mkdir -p docs/archive/

# Move current implementation docs
mv CRYPTO_IMPLEMENTATION.md docs/
mv CRYPTO_QUICKSTART.md docs/
mv IMPLEMENTATION_SUMMARY.md docs/
mv PROTOCOL_AUDIT_REPORT.md docs/
mv AUDIT_SUMMARY.md docs/

# Archive migration history
mv MIGRATION_SUMMARY.txt docs/archive/
mv CHANGELOG_HTTPS.md docs/archive/
mv CHANGES_OVERVIEW.txt docs/archive/
```

---

### 3️⃣ Clean Python Cache

```bash
# Remove all __pycache__
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find . -type f -name "*.pyc" -delete
```

---

### 4️⃣ Update .gitignore

**Copy the optimized .gitignore from `CLEANUP_DIAGNOSTIC_REPORT.md`**

Or quick append missing patterns:

```bash
cat >> .gitignore << 'EOF'

# Additional patterns
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
Thumbs.db
Desktop.ini
._*
*.tmp
*.temp
*.bak
agents.json
logs/
uploads/
downloads/
EOF
```

---

## 📊 Files Summary

### ✅ Keep (Active Code)
- `agent/agent_ngrok.py` ← **CRITICAL**
- `server/server.py` ← **CRITICAL**
- `shared/crypto_utils.py` ← **CRITICAL**
- `test_crypto.py`
- `requirements.txt`
- `README.md`

### ❌ Delete (Obsolete)
- `agent/agent.py` (old TCP)
- `agent/agent_hotspot.py` (old TCP)
- `agent/main.py` (empty)
- `server/main.py` (empty)
- `interface/main.py` (empty)
- `shared/README.md` (empty)
- `interface/` directory (empty)

### ⚠️ Review (Your Decision)
- 15+ markdown files (many duplicates)
- 8+ shell scripts (some obsolete)

---

## 🚨 Safety Checklist

Before cleanup:

- [ ] Backup: `tar -czf backup.tar.gz aligo-c2-frameworkk/`
- [ ] Git commit: `git commit -am "Pre-cleanup snapshot"`

After cleanup:

- [ ] Test server: `cd server && python3 server.py`
- [ ] Test crypto: `python3 test_crypto.py`
- [ ] Test agent: `python3 agent/agent_ngrok.py http://localhost:5000`

---

## 📈 Expected Result

**Before:** 45+ files  
**After:** ~15 files  
**Improvement:** 67% reduction in clutter

---

**Full Details:** Read `CLEANUP_DIAGNOSTIC_REPORT.md`
