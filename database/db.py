"""
ResultOps - Firebase Firestore Database Connection
Replaces Supabase with Firebase Admin SDK.
"""

import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_db = None


def get_client():
    """Returns a cached Firestore client instance."""
    global _db
    if _db is None:
        key_path = os.environ.get("FIREBASE_KEY_PATH", "firebase_key.json")
        if not os.path.exists(key_path):
            raise FileNotFoundError(
                f"Firebase key file not found: '{key_path}'\n"
                "Download it from Firebase Console → Project Settings → Service Accounts → Generate new private key"
            )
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase app initialized")
        _db = firestore.client()
        logger.info("Firestore client ready")
    return _db


def reset_client():
    """Force re-initialisation."""
    global _db
    _db = None
