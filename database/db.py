"""
ResultOps - Firebase DB connection
Supports both local firebase_key.json and Streamlit Cloud secrets.
"""

import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

_db = None


def get_client():
    global _db
    if _db is None:
        if not firebase_admin._apps:
            # ── Streamlit Cloud: load from secrets ──────────────────────────
            try:
                import streamlit as st
                key_dict = dict(st.secrets["firebase"])
                # private_key newlines get escaped in secrets — fix them
                key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(key_dict)
                logger.info("Firebase initialized from Streamlit secrets")

            # ── Local dev: load from firebase_key.json ──────────────────────
            except Exception:
                key_path = os.environ.get("FIREBASE_KEY_PATH", "firebase_key.json")
                if not os.path.exists(key_path):
                    raise FileNotFoundError(
                        f"Firebase key not found: '{key_path}'\n"
                        "Add it as a file locally or via Streamlit Cloud secrets."
                    )
                cred = credentials.Certificate(key_path)
                logger.info(f"Firebase initialized from file: {key_path}")

            firebase_admin.initialize_app(cred)

        _db = firestore.client()
    return _db


def reset_client():
    global _db
    _db = None