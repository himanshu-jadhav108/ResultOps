# ☁️ Hosting ResultOps on Streamlit Cloud

Complete step-by-step guide to deploy ResultOps on [Streamlit Community Cloud](https://share.streamlit.io) — free hosting for public repos.

---

## 📋 Prerequisites

- [x] GitHub account
- [x] ResultOps code pushed to a **public** GitHub repository
- [x] Firebase project set up with Firestore enabled
- [x] Firebase service account key (`firebase_key.json`) downloaded

---

## Step 1: Prepare Your Repository

Make sure these files **ARE** in your repo:

```
✅ app.py
✅ requirements.txt
✅ .streamlit/config.toml
✅ analytics/
✅ database/
✅ parser/
✅ services/
✅ utils/
✅ views/
✅ logo.png
✅ .env.example
```

Make sure these files are **NOT** in your repo (add to `.gitignore`):

```
❌ firebase_key.json
❌ .env
❌ venv/
❌ __pycache__/
```

Your `.gitignore` should contain:
```gitignore
firebase_key.json
.env
venv/
__pycache__/
*.pyc
```

---

## Step 2: Verify `requirements.txt`

Ensure your `requirements.txt` lists all dependencies:

```txt
streamlit>=1.35.0
firebase-admin>=6.4.0
pdfplumber>=0.10.3
pandas>=2.2.0
openpyxl>=3.1.2
python-dotenv>=1.0.0
```

> ⚠️ Do **NOT** include `venv` or system-level packages. Only list what `pip install` should install.

---

## Step 3: Push to GitHub

```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

---

## Step 4: Create Streamlit Cloud Account

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"Sign in with GitHub"**
3. Authorize Streamlit to access your repositories

---

## Step 5: Deploy the App

1. Click **"New app"** button (top right)
2. Fill in the deployment form:

| Field | Value |
|---|---|
| **Repository** | `himanshu-jadhav108/ResultOps` (or your repo name) |
| **Branch** | `main` |
| **Main file path** | `app.py` |

3. Click **"Advanced settings"** before deploying

---

## Step 6: Configure Secrets (Critical!)

In the **Advanced settings** → **Secrets** section, paste the following TOML configuration:

```toml
# ── Passwords (SHA-256 hashes) ────────────────────────────────────
READ_PASSWORD_HASH = "<sha256_hash_of_your_read_password>"
WRITE_PASSWORD_HASH = "<sha256_hash_of_your_write_password>"
ADMIN_PASSWORD_HASH = "<sha256_hash_of_your_admin_password>"

# ── Firebase Service Account Key ─────────────────────────────────
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "123456789012345678901"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"
```

### How to Get the Firebase Values

1. Open your `firebase_key.json` file locally
2. Copy each field into the TOML format above
3. For `private_key`: paste the entire key as a **single line**, replacing actual newlines with `\n`

### Generate Password Hashes

```bash
python -c "import hashlib; print(hashlib.sha256('read@1234'.encode()).hexdigest())"
python -c "import hashlib; print(hashlib.sha256('write@9876'.encode()).hexdigest())"
python -c "import hashlib; print(hashlib.sha256('Himanshu@09'.encode()).hexdigest())"
```

---

## Step 7: Deploy!

1. Click **"Deploy!"** button
2. Wait 2-4 minutes for the app to build and start
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## Step 8: Verify Deployment

After deployment, check:

- [ ] App loads without errors
- [ ] Login with READ password works → Analytics dashboard visible
- [ ] Login with WRITE password works → Upload page functional
- [ ] Login with ADMIN password works → System Stats and Delete visible
- [ ] Theme toggle (dark/light) works
- [ ] PDF upload and parsing works
- [ ] Excel download works
- [ ] Firebase data is being read/written correctly

---

## 🔄 Updating the App

Every time you push to `main`, Streamlit Cloud **auto-deploys** the latest code:

```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```

The app will rebuild automatically within 1-2 minutes.

---

## ⚙️ Managing Secrets After Deployment

1. Go to your app on [share.streamlit.io](https://share.streamlit.io)
2. Click **"⋮" (three dots menu)** on your app → **"Settings"**
3. Navigate to **"Secrets"** tab
4. Edit secrets and click **"Save"**
5. App will **reboot automatically** with new secrets

---

## 🔧 Troubleshooting Deployment

| Issue | Fix |
|---|---|
| **App crashes on start** | Check logs: click "Manage app" → "View logs" |
| **ModuleNotFoundError** | Add missing package to `requirements.txt` and push |
| **Firebase connection fails** | Verify `[firebase]` section in secrets has correct values |
| **Password login not working** | Verify password hashes in secrets match your passwords |
| **`private_key` format error** | Ensure private key is on a single line with `\n` escape chars |
| **App takes too long to start** | Streamlit Cloud has cold-start; first access takes ~30s |
| **App goes to sleep** | Free tier apps sleep after 7 days of inactivity — visit to wake |

---

## 📊 Streamlit Cloud Limits (Free Tier)

| Resource | Limit |
|---|---|
| **Apps per account** | Up to 3 |
| **Repo visibility** | Public repos only |
| **Memory** | ~1 GB |
| **Storage** | Ephemeral (resets on reboot) |
| **Inactivity sleep** | After 7 days |
| **Custom domain** | Not supported (use `.streamlit.app`) |

---

## 🔗 Useful Links

- [Streamlit Cloud Documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [Streamlit Secrets Management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Firebase Admin SDK Docs](https://firebase.google.com/docs/admin/setup)
- [Streamlit Cloud Status](https://status.streamlit.io/)
