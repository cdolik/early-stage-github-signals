# 🔑 GitHub Token Setup & Verification Guide

## What is a Shell?

A **shell** is your command-line interface (on macOS: `zsh`) that runs commands and manages environment variables like your GitHub token.

## ✅ Your Current Security Status: SECURE

Your GitHub Personal Access Token setup follows best practices:

- **Token stored in `.env` file** ✅
- **`.env` is in `.gitignore`** ✅ (prevents accidental commits)
- **Project automatically loads token** ✅

## 🚀 New Features Added

### 1. Quick Token Testing with Makefile

```bash
# Test your GitHub token anytime
make test-token
```

### 2. CLI Token Verification

```bash
# Verify token and exit (useful for troubleshooting)
python3 weekly_gems_cli.py --verify-token

# Or combine with other flags
python3 weekly_gems_cli.py --verify-token --debug
```

### 3. Integrated Testing

Token verification is now part of your test suite:

```bash
make test  # Now includes token testing
```

## 📋 Next Steps Checklist

### ✅ 1. Keep the token safe

- [x] Token stored in `.env` file — perfect
- [x] `.env` is listed in `.gitignore` so it never gets committed
- **Why?** Keeps your token private and secure

### ✅ 2. Use the token in your app

- [x] Scripts automatically use the token via `os.getenv()`
- [x] No need to manually re-enter it every time
- **Why?** Seamless development experience

### 🔄 3. Optional: Set token as Environment Variable in GitHub Actions

If your CI workflows need GitHub API access:

1. Go to **Repo → Settings → Secrets and Variables → Actions**
2. Add it as **Repository Secret** (e.g., `GH_TOKEN`)
3. Use in workflows as `${{ secrets.GH_TOKEN }}`

### 🧪 4. Test a full workflow

Run your pipeline to confirm everything works:

```bash
# Test locally with limited repos
make run-lite

# Generate full report
make run

# Test and validate
make test
```

### 📊 5. Check your GitHub Actions

Monitor workflow status:

- Watch for failed workflows in **Actions** tab
- Confirm these are active: `weekly-pipeline.yml`, `test-and-validate.yml`, `cleanup-branches.yml`
- Check README badges for real-time status

## 🛠️ Available Commands

| Command                                     | Purpose                               |
| ------------------------------------------- | ------------------------------------- |
| `make test-token`                           | Quick token validation                |
| `python3 weekly_gems_cli.py --verify-token` | CLI token verification                |
| `python3 scripts/test_github_token.py`      | Detailed token testing                |
| `make test`                                 | Full test suite (includes token test) |

## 🔐 Security Best Practices

### ✅ What You're Doing Right

- Token in `.env` file (not hardcoded)
- `.env` file properly ignored by git
- Token validation before use
- Partial token logging for debugging

### 🔄 Recommended Maintenance

- **Rotate token every 3-6 months**
- **Set expiration dates** at [GitHub Settings → Tokens](https://github.com/settings/tokens)
- **Use minimum required permissions** for security
- **Monitor rate limits** (you have 5000 API calls/hour)

## 🆘 Troubleshooting

### Token Issues

```bash
# Test your token
make test-token

# Get detailed info
python3 weekly_gems_cli.py --verify-token --debug

# Check environment
python3 -c "import os; print('Token found:', bool(os.getenv('GITHUB_TOKEN')))"
```

### Common Problems

- **"No token found"** → Check `.env` file exists and has `GITHUB_TOKEN=your_token`
- **"Token invalid"** → Check token at [GitHub Settings](https://github.com/settings/tokens)
- **"Rate limit exceeded"** → Wait or use a different token

---

**You're all set!** 🎉 Your token setup is secure and ready for development.
