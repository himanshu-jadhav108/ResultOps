<div align="center">

<!-- Replace with your actual logo once uploaded to GitHub -->
<img src="logo.png" alt="ResultOps Logo" width="380"/>

<br/><br/>

# ResultOps 🎓

**University-grade result processing platform — built for SPPU affiliated colleges**

<<<<<<< HEAD
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Live App](https://img.shields.io/badge/Live%20App-Streamlit%20Cloud-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://your-app-url.streamlit.app)
=======
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Live App](https://img.shields.io/badge/Live%20App-Streamlit%20Cloud-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://your-app-url.streamlit.app)
![CI](https://github.com/himanshu-jadhav108/ResultOps/actions/workflows/ci.yml/badge.svg)
>>>>>>> origin/develop

<br/>

> Parse · Validate · Analyse · Export — all in one platform.

</div>

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| 📄 **Automated PDF Parsing** | Extracts structured student data from text-based university ledger PDFs using `pdfplumber` |
| 🔍 **Dynamic Metadata Detection** | Auto-detects university, college, department, session, and semester — zero hardcoding |
| 🧬 **Dynamic Subject Detection** | Subject codes detected at runtime — works for any department, any semester |
| 🚫 **Duplicate Protection** | Prevents re-upload of the same semester using a composite key check |
| ✅ **Pre-save Validation** | Validates SGPA consistency, PRN format, and subject counts before saving |
<<<<<<< HEAD
| 📊 **Analytics Dashboard** | Pass/fail stats, SGPA distribution, subject-wise analytics, and ranked student lists |
| 📥 **Instant Excel Export** | Styled 5-sheet workbook downloadable before and after saving — no DB required |
| 📋 **History Management** | View, audit, and admin-delete previously uploaded semesters |
| 🔥 **Firebase Backend** | Google Firebase Firestore — reliable, fast, reachable from any network |
=======
| 📊 **Analytics Dashboard** | Pass/fail stats, SGPA distribution, subject-wise analytics, ranked student lists, and subject difficulty scoring |
| 📥 **Selective Excel Export** | Choose which sheets to include — Summary, Rank List, Subject Analytics, SGPA Distribution |
| 📋 **History Management** | View, audit, and admin-delete previously uploaded semesters |
| 🔥 **Firebase Backend** | Google Firebase Firestore — reliable, fast, reachable from any network |
| 🎨 **Dark / Light Theme** | Toggle between dark navy and clean white theme with a single click |
| 🔐 **3-Tier Authentication** | Separate READ, WRITE, and ADMIN passwords with admin-only features |
| 📈 **Semester Comparison** | Compare multiple semesters side-by-side with trend analysis |
| 📚 **Subject Difficulty** | Weighted difficulty scoring: `(Fail% × 0.6) + ((100 − AvgMarks) × 0.4)` |
>>>>>>> origin/develop

---

## 🗂️ Project Structure

```
ResultOps/
<<<<<<< HEAD
├── app.py                      # Streamlit multi-page application (entry point)
├── logo.png                    # App logo shown in sidebar and README
├── firebase_key.json           # Firebase service account key (NOT in git)
├── .env                        # Environment variables (NOT in git)
├── requirements.txt            # Python dependencies
├── test_connection.py          # Firebase connectivity test script
|
│
├── parser/                     # PDF extraction and parsing
│   ├── pdf_parser.py           # Text extraction via pdfplumber
│   ├── metadata_extractor.py   # Detects university/college/dept/session/semester
│   └── student_parser.py       # Parses individual student records dynamically
│
├── database/
│   └── db.py                   # Firebase Admin SDK client (singleton + Streamlit secrets)
│
├── analytics/
│   └── analytics.py            # Firestore-based analytics and filter helpers
│
├── services/
│   ├── result_service.py       # Firestore writes, batch inserts, duplicate guard
│   └── excel_export.py         # Styled multi-sheet Excel workbook generator
│
└── utils/
    └── validators.py           # Pre-save data validation routines
=======
├── app.py                          # Streamlit entry point — routing, theme, auth, sidebar
├── logo.png                        # App logo (sidebar + README)
├── setup.cfg                       # Tool configuration (flake8, mypy, pytest)
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Dev dependencies (testing, linting, security)
├── .env.example                    # Environment variable template
│
├── parser/                         # PDF extraction & parsing pipeline
│   ├── __init__.py
│   ├── pdf_parser.py               # Raw text extraction via pdfplumber
│   ├── metadata_extractor.py       # University, college, department, session detection
│   ├── student_parser.py           # Student block splitting + subject line parsing
│   └── refactored_parser.py        # Unified pipeline — orchestrates metadata + students + confidence
│
├── database/
│   ├── __init__.py
│   └── db.py                       # Firebase Admin SDK client (Streamlit secrets + .env fallback)
│
├── analytics/
│   ├── __init__.py
│   └── analytics.py                # Queries, ranking, comparison, difficulty, SGPA distribution
│
├── services/
│   ├── __init__.py
│   ├── result_service.py           # Firestore writes, batch inserts, duplicate guard
│   └── excel_export.py             # Styled multi-sheet Excel workbook generator
│
├── views/                          # Streamlit page views
│   ├── __init__.py
│   ├── upload_page.py              # PDF upload, parse preview, validation, save, inline Excel export
│   ├── analytics_page.py           # Dashboard — charts, tables, view toggle, selective Excel download
│   ├── history_page.py             # Upload history + admin-only delete
│   └── system_stats.py             # System statistics (admin-only)
│
├── utils/
│   ├── __init__.py
│   ├── theme.py                    # Dark/light theme manager with full CSS injection
│   ├── auth.py                     # 3-tier authentication (READ / WRITE / ADMIN)
│   └── validators.py               # Pre-save data validation (SGPA, PRN, subjects)
│
├── test/
│   ├── __init__.py
│   ├── test_parser.py              # Unit + integration tests for parser and ranking
│   └── test_connection.py          # Firebase connectivity check script
│
├── .github/workflows/
│   └── ci.yml                      # GitHub Actions CI — black, flake8, mypy, pytest, bandit
│
├── .streamlit/
│   └── config.toml                 # Streamlit server configuration
│
├── docs/
│   ├── hosting.md                  # Step-by-step Streamlit Cloud deployment guide
│   └── github_actions.md           # GitHub Actions CI/CD setup guide
│
└── hash_password/                  # Utility to generate SHA-256 password hashes
>>>>>>> origin/develop
```

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    classDef user      fill:#1a4a8a,stroke:#2d8cff,stroke-width:2px,color:#e8f0fe
    classDef parser    fill:#7c4a00,stroke:#f5a623,stroke-width:2px,color:#fff8ee
    classDef validate  fill:#7a0022,stroke:#ff4d6d,stroke-width:2px,color:#ffe8ec
    classDef firebase  fill:#004d2e,stroke:#00d97e,stroke-width:2px,color:#e0fff4
    classDef analytics fill:#3b1f7a,stroke:#a78bfa,stroke-width:2px,color:#f0ebff
    classDef export    fill:#004a4a,stroke:#06d6c7,stroke-width:2px,color:#e0fffe
    classDef decision  fill:#1a3a1a,stroke:#00d97e,stroke-width:2px,color:#e0fff4

    subgraph USER["👤  USER LAYER"]
        direction LR
        A["👤 Faculty / Admin"]
<<<<<<< HEAD
        B["🖥️ Streamlit Web App\napp.py · Port 8501\n4 Pages: Upload · Dashboard · Export · History"]
=======
        B["🖥️ Streamlit Web App<br/>app.py · Port 8501"]
    end

    subgraph PAGES["📑  PAGE VIEWS"]
        direction LR
        P1["📤 Upload Page<br/>upload_page.py"]
        P2["📊 Analytics Page<br/>analytics_page.py"]
        P3["📋 History Page<br/>history_page.py"]
        P4["⚙️ System Stats<br/>system_stats.py"]
>>>>>>> origin/develop
    end

    subgraph PARSE["📄  PDF PROCESSING LAYER"]
        direction LR
<<<<<<< HEAD
        C["📄 PDF Parser\npdf_parser.py"]
        D["🔍 Metadata Extractor\nmetadata_extractor.py"]
        E["👥 Student Parser\nstudent_parser.py"]
    end

    subgraph VALID["🧪  VALIDATION LAYER"]
        direction LR
        F["🧪 Data Validator\nvalidators.py"]
        G{"🚫 Duplicate Guard\nSemester Key Lookup"}
        H["🔐 Auth & Config\ndb.py + .env"]
    end

    subgraph FIRE["🔥  DATABASE — FIREBASE FIRESTORE"]
        direction LR
        I["🔥 Firebase Admin SDK\ndb.py · asia-south1"]
        J["📁 semesters collection\nDoc ID = semester_key"]
        K["📋 results collection\nOne doc per student"]
    end

    subgraph OUT["📊  ANALYTICS & OUTPUT LAYER"]
        direction LR
        L["📊 Analytics Engine\nanalytics.py"]
        M["📥 Excel Export\nexcel_export.py · 5 Sheets"]
        N["⬇️ Browser Download\n.xlsx"]
    end

    A -->|Upload PDF| B
    B -->|PDF bytes| C
    C -->|Full text| D
    D -->|PDFMetadata| E
    E -->|StudentRecord list| F
    F -->|Passed| G
    G -->|❌ Exists| B
    G -->|✅ New| I
    H -.->|Credentials| I
    I -->|batch write| J
    I -->|batch write × N| K
    K -->|query| L
    J -.->|metadata| L
    L -->|DataFrames| B
    L --> M
    M --> N

    class A,B user
    class C,D,E parser
    class F,H validate
    class G decision
    class I,J,K firebase
    class L analytics
    class M,N export
=======
        C["📄 PDF Parser<br/>pdf_parser.py<br/>pdfplumber text extraction"]
        D["🔍 Metadata Extractor<br/>metadata_extractor.py<br/>University · College · Dept · Sem"]
        E["👥 Student Parser<br/>student_parser.py<br/>PRN · SGPA · Subjects"]
        F["🔗 Unified Pipeline<br/>refactored_parser.py<br/>Orchestrator + Confidence Score"]
    end

    subgraph AUTH["🔐  AUTH + VALIDATION"]
        direction LR
        G["🔐 3-Tier Auth<br/>auth.py<br/>READ · WRITE · ADMIN"]
        H["🧪 Data Validator<br/>validators.py"]
        I{"🚫 Duplicate Guard<br/>Semester Key Check"}
    end

    subgraph FIRE["🔥  FIREBASE FIRESTORE"]
        direction LR
        J["🔥 Firebase SDK<br/>db.py"]
        K["📁 semesters<br/>collection"]
        L["📋 results<br/>collection"]
    end

    subgraph OUT["📊  ANALYTICS + EXPORT"]
        direction LR
        M["📊 Analytics Engine<br/>analytics.py<br/>Ranking · Comparison · Difficulty"]
        N["📥 Excel Export<br/>excel_export.py<br/>Selective · Styled · Multi-sheet"]
        O["⬇️ Browser Download<br/>.xlsx"]
    end

    A -->|"Login"| G
    G -->|"Authenticated"| B
    B --> P1 & P2 & P3 & P4

    P1 -->|"Upload PDF"| C
    C -->|"Raw text"| F
    F --> D & E
    D -->|"PDFMetadata"| F
    E -->|"StudentRecord list"| F

    F -->|"Parsed data"| H
    H -->|"Validated"| I
    I -->|"❌ Exists"| P1
    I -->|"✅ New"| J

    J -->|"batch write"| K
    J -->|"batch write × N"| L

    P2 -->|"Query"| M
    L -->|"docs"| M
    K -.-|"metadata"| M
    M -->|"DataFrames"| P2
    M --> N
    N --> O

    P3 -->|"List/Delete"| J
    P4 -->|"Stats"| J

    class A,B user
    class P1,P2,P3,P4 user
    class C,D,E,F parser
    class G,H validate
    class I decision
    class J,K,L firebase
    class M analytics
    class N,O export
>>>>>>> origin/develop
```

**Upload Data Flow:**
```
<<<<<<< HEAD
PDF Upload → Text Extract → Metadata Detect → Student Parse
=======
PDF Upload → Text Extract → Metadata Detect → Student Parse → Confidence Score
>>>>>>> origin/develop
    → Validate → Duplicate Check → Firestore Write → Excel Export
```

**Firestore Collections:**

| Collection | Doc ID | Contents |
|---|---|---|
| `semesters` | `University\|College\|Dept\|Sem\|Session\|Year` | Metadata + student count |
| `results` | Auto-generated | PRN, SGPA, Status, `subjects[]` nested array |

---

<<<<<<< HEAD
=======
## 🔐 Security & Authentication

ResultOps uses **3-tier password authentication**, all hashed with **SHA-256**:

| Tier | Access Level | Features |
|---|---|---|
| 🟢 **READ** | View-only analytics | Dashboard, analytics, history (view only) |
| 🟡 **WRITE** | Upload & save data | Upload PDF, parse, save to database |
| 🔴 **ADMIN** | Full control | System Stats, delete records from History |

### Setting Up Passwords

1. Generate SHA-256 hashes for your passwords:
   ```bash
   python -c "import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())"
   ```

2. Add hashes to `.env`:
   ```env
   READ_PASSWORD_HASH=<sha256_hash_of_read_password>
   WRITE_PASSWORD_HASH=<sha256_hash_of_write_password>
   ADMIN_PASSWORD_HASH=<sha256_hash_of_admin_password>
   ```

### Current Defaults (`.env.example`)

| Role | Default Password |
|---|---|
| READ | `password` |
| WRITE | `password` |
| ADMIN | `password` |

> ⚠️ **Change these immediately** after first setup.

---

>>>>>>> origin/develop
## 🛠️ Setup Instructions

### 1. Clone & Install

```bash
git clone https://github.com/himanshu-jadhav108/ResultOps.git
cd ResultOps
<<<<<<< HEAD
=======
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

>>>>>>> origin/develop
pip install -r requirements.txt
```

### 2. Create Firebase Project

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. **Add Project** → name it `ResultOps` → disable Analytics → **Create Project**

### 3. Enable Firestore

1. **Build** → **Firestore Database** → **Create Database**
2. Choose **Start in test mode** → Region: **asia-south1 (Mumbai)** → **Enable**

### 4. Download Service Account Key

1. ⚙️ gear icon → **Project Settings** → **Service Accounts**
2. **Generate new private key** → **Generate Key**
<<<<<<< HEAD
3. Rename to `firebase_key.json` → place in `ResultOps/` root folder
=======
3. Rename to `firebase_key.json` → place in project root
>>>>>>> origin/develop

> ⚠️ **Never commit `firebase_key.json` to GitHub.** Already in `.gitignore`.

### 5. Configure Environment

```bash
cp .env.example .env
```

<<<<<<< HEAD
```env
FIREBASE_KEY_PATH=firebase_key.json
ADMIN_PASSWORD=your_secure_password_here
```

### 6. Test Connection

```bash
python test_connection.py
```

```
✅ Key file found
✅ Firestore connected successfully!
🎉 Everything is working! Run: streamlit run app.py
```

### 7. Run the App
=======
Edit `.env` with your password hashes:
```env
FIREBASE_KEY_PATH=firebase_key.json
READ_PASSWORD_HASH=<your_read_hash>
WRITE_PASSWORD_HASH=<your_write_hash>
ADMIN_PASSWORD_HASH=<your_admin_hash>
```

### 6. Run the App
>>>>>>> origin/develop

```bash
streamlit run app.py
```

Open **http://localhost:8501**

---

<<<<<<< HEAD
## ☁️ Deploy to Streamlit Cloud

1. Push code to GitHub *(without `firebase_key.json` or `.env`)*
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo → `main` branch → `app.py`
4. Click **Advanced settings** → **Secrets** and paste:

```toml
ADMIN_PASSWORD = "your_password"

[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

5. Click **Deploy** — live in ~3 minutes 🚀
=======
## 🎨 Theme System

ResultOps has a built-in **dark/light theme toggle**:

| Theme | Background | Sidebar | Text |
|---|---|---|---|
| 🌙 **Dark** | Navy `#060e1f` | Gradient navy→blue | White `#e8f0fe` |
| ☀️ **Light** | Soft grey `#f4f7fb` | Same dark gradient | Dark `#0f1e3a` |

Toggle via the sidebar button — all elements are fully styled for both themes.

---

## 📊 Analytics Dashboard Features

| Feature | Description |
|---|---|
| 📈 **Semester Overview** | 6 key metrics: students, avg SGPA, highest, distinctions, pass count/% |
| 📉 **SGPA Distribution** | Bar chart + table with percentage breakdown |
| 🏆 **Student Rankings** | Top 10 highlighted list, full rank list in expander, fail list |
| 📚 **Subject Analytics** | Pass %, average marks, highest/lowest per subject with color-coded table |
| 👁️ **View Mode Toggle** | Switch between Charts Only / Tables Only / Both — fully reversible |
| ⬇️ **Selective Excel Download** | Choose sheets: Summary, Rank List, Subject Analytics, SGPA Distribution |
>>>>>>> origin/develop

---

## 📄 PDF Requirements

Requires **text-based** (not scanned) SPPU ledger PDFs. Structure:

```
PRN: XXXXX  SEAT NO.: YYY  NAME: Student Name
SEMESTER: 5

<<<<<<< HEAD
410241  45  18  20  --  --  83  4  O  10  40
=======
410241  45  18  20  --  83  4  O  10  40
>>>>>>> origin/develop
...

Winter Session 2025 SGPA : 8.50  Credits Earned/Total : 24/24
SGPA: (SEM-5) 8.50
```

> **Quick check:** Open PDF in Adobe Reader → try to select/copy text. If it works, ResultOps can parse it.

---

<<<<<<< HEAD
## 📥 Excel Report — 5 Sheets

| Sheet | Contents |
|---|---|
| 📋 **Student Master** | All students: PRN, Seat No, Name, SGPA, Credits, Status, Category |
| 🏆 **Rank List** | Sorted by SGPA with Distinction / First Class / Pass labels |
| 📚 **Subject Analytics** | Per-subject: Appeared, Passed, Failed, Pass %, Highest, Lowest, Average |
| 📊 **SGPA Distribution** | Count in each SGPA range (Fail / Pass / Second / First / Distinction) |
| 📝 **Summary** | Overall stats: average SGPA, pass %, distinctions, total subjects |

Reports available **before and after** saving to database.

---

=======
>>>>>>> origin/develop
## 🔒 Environment Variables

| Variable | Description |
|---|---|
| `FIREBASE_KEY_PATH` | Path to Firebase service account JSON key |
<<<<<<< HEAD
| `ADMIN_PASSWORD` | Password for admin delete operations in History page |
=======
| `READ_PASSWORD_HASH` | SHA-256 hash for read-only access |
| `WRITE_PASSWORD_HASH` | SHA-256 hash for upload/write access |
| `ADMIN_PASSWORD_HASH` | SHA-256 hash for admin access (stats, delete) |

---

## 🧪 CI/CD Pipeline

The GitHub Actions CI pipeline runs on every push to `main` and `develop`:

| Step | Tool | What it checks |
|---|---|---|
| Formatting | `black --check .` | Code style consistency |
| Lint (strict) | `flake8 --select=E9,F63,F7,F82` | Syntax errors, undefined names |
| Lint (warnings) | `flake8 --exit-zero` | Line length, complexity (non-blocking) |
| Type Check | `mypy` | Type annotations in `parser/`, `utils/`, `analytics/` |
| Tests | `pytest test/ -v` | 12 unit + integration tests |
| Security | `bandit -ll` | Common security vulnerabilities |
>>>>>>> origin/develop

---

## ⚡ Performance

| Operation | Target |
|---|---|
| Parse 100 students from PDF | < 5 seconds |
| Firestore batch write (100 students) | < 3 seconds |
| Analytics query | < 1 second |

---

## 🔧 Troubleshooting

| Error | Fix |
|---|---|
<<<<<<< HEAD
| `FileNotFoundError: firebase_key.json` | Place key file in `ResultOps/` folder |
| `Invalid service account certificate` | Re-download key from Firebase Console |
| `TransportError` / network failure | Switch to mobile hotspot |
=======
| `FileNotFoundError: firebase_key.json` | Place key file in project root |
| `Invalid service account certificate` | Re-download key from Firebase Console |
| `TransportError` / network failure | Check internet, switch to mobile hotspot |
>>>>>>> origin/develop
| `PermissionDenied` | Set Firestore rules to test mode |
| `0 students detected` | PDF must be text-based, not scanned |
| `Semester not detected` | PDF must contain `SEMESTER: N` pattern |
| Sidebar shows raw HTML | Run `pip install --upgrade streamlit` |
<<<<<<< HEAD

Full details in **[GUIDE.md](GUIDE.md)**
=======
| Light theme text invisible | Clear browser cache, hard refresh (`Ctrl+Shift+R`) |

---

## 📚 Additional Documentation

| Document | Description |
|---|---|
| [**hosting.md**](docs/hosting.md) | Step-by-step guide to deploy on Streamlit Cloud |
| [**github_actions.md**](docs/github_actions.md) | GitHub Actions CI/CD pipeline setup |
>>>>>>> origin/develop

---

## 🛡️ Security Notes

- Firebase key used server-side only via `firebase-admin` SDK
- `firebase_key.json` in `.gitignore` — never committed to version control
<<<<<<< HEAD
- Admin password gates all destructive operations
=======
- All passwords stored as SHA-256 hashes — no plaintext anywhere
- Admin password gates destructive operations (delete, system stats)
>>>>>>> origin/develop
- Firestore in test mode for dev — restrict rules before going to production

---

## 👨‍💻 About the Maintainer

<div align="center">

**Himanshu Jadhav**
*Second-Year Engineering Student — AI & Data Science*

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-himanshu--jadhav108-181717?style=for-the-badge&logo=github)](https://github.com/himanshu-jadhav108)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Himanshu%20Jadhav-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/himanshu-jadhav-328082339)
[![Instagram](https://img.shields.io/badge/Instagram-himanshu__jadhav__108-E4405F?style=for-the-badge&logo=instagram)](https://www.instagram.com/himanshu_jadhav_108)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit%20Now-F7B731?style=for-the-badge&logo=vercel)](https://himanshu-jadhav-portfolio.vercel.app/)

<br/>

*Built with ❤️ for Savitribai Phule Pune University affiliated colleges*

</div>

---

<div align="center">
<<<<<<< HEAD
<sub>© 2025 Himanshu Jadhav · ResultOps v1.0 · Firebase Edition</sub>
=======
<sub>© 2025 Himanshu Jadhav · ResultOps v2.0 · Firebase Edition</sub>
>>>>>>> origin/develop
</div>
