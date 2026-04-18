"""
ResultOps - Firebase Connection Test
Run this before starting the app to verify Firebase connectivity.
Usage: python test_connection.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 55)
print("  ResultOps — Firebase Connection Test")
print("=" * 55)

key_path = os.environ.get("FIREBASE_KEY_PATH", "firebase_key.json")
print(f"Key file path : {key_path}")

if not os.path.exists(key_path):
    print(f"\n❌ Key file NOT found: {key_path}")
    print("\nFix: Download it from Firebase Console")
    print("  → Project Settings → Service Accounts → Generate new private key")
    print("  → Save it as 'firebase_key.json' in the ResultOps folder")
    sys.exit(1)

print("[OK] Key file found")
print("\nConnecting to Firebase...")

try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Test read
    db.collection("semesters").limit(1).get()
    print("[OK] Firestore connected successfully!")
    print("[OK] Database read test passed!")
    print()
    print("Everything is working! Run:")
    print("   streamlit run app.py")

except Exception as e:
    print(f"\n[ERROR] Connection failed: {e}")
    print("\nCommon causes:")
    print("  - Wrong or corrupted firebase_key.json file")
    print("  - Firestore not enabled in your Firebase project")
    print("  - Internet connection issue")
    sys.exit(1)
