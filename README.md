<div align="center">

<!-- Replace with your actual logo once uploaded to GitHub -->
<img src="logo.png" alt="ResultOps Logo" width="380"/>

<br/><br/>

# ResultOps 🎓

**University-grade result processing platform — built for SPPU affiliated colleges**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=black)](https://firebase.google.com)
[![Live App](https://img.shields.io/badge/Live%20App-Streamlit%20Cloud-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://your-app-url.streamlit.app)

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
| 📊 **Analytics Dashboard** | Pass/fail stats, SGPA distribution, subject-wise analytics, and ranked student lists |
| 📥 **Instant Excel Export** | Styled 5-sheet workbook downloadable before and after saving — no DB required |
| 📋 **History Management** | View, audit, and admin-delete previously uploaded semesters |
| 🔥 **Firebase Backend** | Google Firebase Firestore — reliable, fast, reachable from any network |

---

## 🗂️ Project Structure

```
ResultOps/
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
        B["🖥️ Streamlit Web App\napp.py · Port 8501\n4 Pages: Upload · Dashboard · Export · History"]
    end

    subgraph PARSE["📄  PDF PROCESSING LAYER"]
        direction LR
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
```

**Upload Data Flow:**
```
PDF Upload → Text Extract → Metadata Detect → Student Parse
    → Validate → Duplicate Check → Firestore Write → Excel Export
```

**Firestore Collections:**

| Collection | Doc ID | Contents |
|---|---|---|
| `semesters` | `University\|College\|Dept\|Sem\|Session\|Year` | Metadata + student count |
| `results` | Auto-generated | PRN, SGPA, Status, `subjects[]` nested array |

---

## 🛠️ Setup Instructions

### 1. Clone & Install

```bash
git clone https://github.com/himanshu-jadhav108/ResultOps.git
cd ResultOps
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
3. Rename to `firebase_key.json` → place in `ResultOps/` root folder

> ⚠️ **Never commit `firebase_key.json` to GitHub.** Already in `.gitignore`.

### 5. Configure Environment

```bash
cp .env.example .env
```

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

```bash
streamlit run app.py
```

Open **http://localhost:8501**

---

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

---

## 📄 PDF Requirements

Requires **text-based** (not scanned) SPPU ledger PDFs. Structure:

```
PRN: XXXXX  SEAT NO.: YYY  NAME: Student Name
SEMESTER: 5

410241  45  18  20  --  --  83  4  O  10  40
...

Winter Session 2025 SGPA : 8.50  Credits Earned/Total : 24/24
SGPA: (SEM-5) 8.50
```

> **Quick check:** Open PDF in Adobe Reader → try to select/copy text. If it works, ResultOps can parse it.

---

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

## 🔒 Environment Variables

| Variable | Description |
|---|---|
| `FIREBASE_KEY_PATH` | Path to Firebase service account JSON key |
| `ADMIN_PASSWORD` | Password for admin delete operations in History page |

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
| `FileNotFoundError: firebase_key.json` | Place key file in `ResultOps/` folder |
| `Invalid service account certificate` | Re-download key from Firebase Console |
| `TransportError` / network failure | Switch to mobile hotspot |
| `PermissionDenied` | Set Firestore rules to test mode |
| `0 students detected` | PDF must be text-based, not scanned |
| `Semester not detected` | PDF must contain `SEMESTER: N` pattern |
| Sidebar shows raw HTML | Run `pip install --upgrade streamlit` |

Full details in **[GUIDE.md](GUIDE.md)**

---

## 🛡️ Security Notes

- Firebase key used server-side only via `firebase-admin` SDK
- `firebase_key.json` in `.gitignore` — never committed to version control
- Admin password gates all destructive operations
- Firestore in test mode for dev — restrict rules before going to production

---

## 👨‍💻 About the Maintainer

<div align="center">

**Himanshu Jadhav**
*Second-Year Engineering Student — AI & Data Science*
*JSPM Narhe Technical Campus, Pune*

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
<sub>© 2025 Himanshu Jadhav · ResultOps v1.0 · Firebase Edition</sub>
</div>
