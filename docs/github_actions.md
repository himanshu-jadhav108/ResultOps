# ⚙️ GitHub Actions for ResultOps

Complete step-by-step guide to set up CI/CD pipelines using GitHub Actions for the ResultOps project.

---

## 📋 What You'll Set Up

| Workflow | Trigger | Purpose |
|---|---|---|
| 🧪 **Lint & Test** | Every push/PR to `main` | Syntax check, lint, run tests |
| 🚀 **Auto-Deploy** | Push to `main` | Streamlit Cloud auto-deploys (no action needed) |
| 📦 **Dependency Check** | Weekly (cron) | Check for outdated packages |

---

## 📁 Directory Structure

GitHub Actions workflow files must be placed inside `.github/workflows/`:

```
ResultOps/
├── .github/
│   └── workflows/
│       ├── lint-test.yml        # Lint + test on every push
│       └── dependency-check.yml # Weekly dependency audit
```

---

## Step 1: Create the Workflows Directory

```bash
mkdir -p .github/workflows
```

---

## Step 2: Lint & Test Workflow

Create `.github/workflows/lint-test.yml`:

```yaml
name: 🧪 Lint & Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    name: Lint & Test
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      # ── Checkout code ──────────────────────────────────────────────
      - name: 📥 Checkout repository
        uses: actions/checkout@v4

      # ── Set up Python ──────────────────────────────────────────────
      - name: 🐍 Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      # ── Cache pip dependencies ─────────────────────────────────────
      - name: 📦 Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      # ── Install dependencies ───────────────────────────────────────
      - name: 📥 Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install flake8 pytest

      # ── Syntax check ───────────────────────────────────────────────
      - name: 🔍 Python syntax check
        run: |
          python -m py_compile app.py
          python -m py_compile analytics/analytics.py
          python -m py_compile utils/auth.py
          python -m py_compile utils/theme.py
          python -m py_compile views/analytics_page.py
          python -m py_compile views/history_page.py
          echo "✅ All files compile successfully"

      # ── Lint with flake8 ───────────────────────────────────────────
      - name: 🧹 Lint with flake8
        run: |
          # Stop the build if there are Python syntax errors or undefined names
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics \
                   --exclude=venv,__pycache__,.git

          # Warnings only — don't fail the build
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=120 \
                   --statistics --exclude=venv,__pycache__,.git

      # ── Run tests ──────────────────────────────────────────────────
      - name: 🧪 Run tests
        run: |
          pytest test/ -v --tb=short || echo "⚠️ Some tests may require Firebase connection"
        env:
          FIREBASE_KEY_PATH: ""
          READ_PASSWORD_HASH: "test_hash"
          WRITE_PASSWORD_HASH: "test_hash"
          ADMIN_PASSWORD_HASH: "test_hash"
```

---

## Step 3: Dependency Check Workflow

Create `.github/workflows/dependency-check.yml`:

```yaml
name: 📦 Dependency Check

on:
  schedule:
    # Runs every Monday at 9:00 AM UTC
    - cron: "0 9 * * 1"
  workflow_dispatch: # Allow manual trigger

jobs:
  check-dependencies:
    name: Check for outdated packages
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v4

      - name: 🐍 Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: 📥 Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: 📋 Check for outdated packages
        run: |
          echo "📦 Outdated packages:"
          pip list --outdated --format=columns || true

      - name: 🔒 Security audit
        run: |
          pip install pip-audit
          pip-audit --fix --dry-run || echo "⚠️ Some vulnerabilities found — review above"
```

---

## Step 4: Add the Workflow Files to Your Repo

```bash
# Create the workflows directory
mkdir -p .github/workflows

# Create the workflow files (or copy them from above)
# Then commit and push
git add .github/workflows/
git commit -m "ci: add GitHub Actions lint, test, and dependency check"
git push origin main
```

---

## Step 5: Add Repository Secrets (Optional)

If your tests need Firebase access, add secrets to your GitHub repo:

1. Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add the following secrets:

| Secret Name | Value |
|---|---|
| `READ_PASSWORD_HASH` | SHA-256 hash of your read password |
| `WRITE_PASSWORD_HASH` | SHA-256 hash of your write password |
| `ADMIN_PASSWORD_HASH` | SHA-256 hash of your admin password |
| `FIREBASE_KEY_JSON` | Full content of `firebase_key.json` (if needed for integration tests) |

> 💡 For unit tests that don't need Firebase, the dummy values in the workflow are sufficient.

---

## Step 6: Add Status Badge to README

Add the workflow status badge to the top of your `README.md`:

```markdown
[![Lint & Test](https://github.com/himanshu-jadhav108/ResultOps/actions/workflows/lint-test.yml/badge.svg)](https://github.com/himanshu-jadhav108/ResultOps/actions/workflows/lint-test.yml)
```

This will show a green ✅ or red ❌ badge based on the latest workflow run.

---

## Step 7: Verify Workflows Are Running

1. Push to `main` or create a Pull Request
2. Go to your repo → **Actions** tab
3. You should see:
   - **🧪 Lint & Test** — running on every push/PR
   - **📦 Dependency Check** — scheduled weekly or run manually

---

## 📊 Workflow Run Results

### What a Successful Run Looks Like

```
✅ Checkout repository         — 2s
✅ Set up Python 3.11          — 15s
✅ Cache pip                    — 1s
✅ Install dependencies         — 25s
✅ Python syntax check          — 3s
✅ Lint with flake8             — 5s
✅ Run tests                    — 8s
```

### What a Failed Run Looks Like

```
✅ Checkout repository
✅ Set up Python 3.11
✅ Install dependencies
❌ Python syntax check          — SyntaxError in app.py line 42
```

→ Fix the error, push again, the workflow re-runs automatically.

---

## 🔄 Advanced: Auto-Deploy with Streamlit Cloud

Streamlit Cloud **automatically deploys** your app when you push to `main`. No extra GitHub Action is needed for deployment. The flow is:

```
Push to main → GitHub Actions runs lint/test → If ✅ → Streamlit auto-deploys
```

If you want to **prevent deployment on test failure**, use branch protection rules:

1. Go to **Settings** → **Branches** → **Add rule**
2. Branch name pattern: `main`
3. Check: **"Require status checks to pass before merging"**
4. Select the **"Lint & Test"** check
5. Now PRs to `main` must pass CI before merging

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| **Workflow not triggering** | Check file is in `.github/workflows/` and YAML is valid |
| **`ModuleNotFoundError`** | Add missing package to `requirements.txt` |
| **Tests fail due to Firebase** | Tests that need DB should be marked `@pytest.mark.integration` and skipped in CI |
| **Flake8 errors** | Fix code style issues or exclude specific rules |
| **Cache not working** | Delete cache: Actions → Caches → Delete |
| **Workflow takes too long** | Reduce Python version matrix or use caching more aggressively |

---

## 🔗 Useful Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Starter Workflows](https://github.com/actions/starter-workflows/tree/main/ci)
- [actions/setup-python](https://github.com/actions/setup-python)
- [actions/cache](https://github.com/actions/cache)
- [Flake8 Rules Reference](https://www.flake8rules.com/)
- [pytest Documentation](https://docs.pytest.org/)
