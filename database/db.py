"""
ResultOps - Firebase DB connection
Supports both Streamlit Cloud secrets and local firebase_key.json
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
            cred = _get_credentials()
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db


def _get_credentials():
    """
    Load Firebase credentials.
    Priority:
      1. Streamlit Cloud secrets  (when deployed)
      2. Local firebase_key.json  (when running locally)
    """

    # ── Try Streamlit secrets first ──────────────────────────────────────────
    in_streamlit_cloud = os.environ.get("STREAMLIT_SHARING_MODE") or \
                         os.environ.get("IS_STREAMLIT_CLOUD") or \
                         _has_streamlit_secrets()

    if in_streamlit_cloud:
        try:
            import streamlit as st
            firebase_secrets = st.secrets["firebase"]

            key_dict = {
                "type":                        firebase_secrets["type"],
                "project_id":                  firebase_secrets["project_id"],
                "private_key_id":              firebase_secrets["private_key_id"],
                "private_key":                 firebase_secrets["private_key"].replace("\\n", "\n"),
                "client_email":                firebase_secrets["client_email"],
                "client_id":                   firebase_secrets["client_id"],
                "auth_uri":                    firebase_secrets["auth_uri"],
                "token_uri":                   firebase_secrets["token_uri"],
                "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
                "client_x509_cert_url":        firebase_secrets["client_x509_cert_url"],
            }

            logger.info("Firebase: loaded from Streamlit secrets")
            return credentials.Certificate(key_dict)

        except KeyError as e:
            raise KeyError(
                f"Missing key in Streamlit secrets: {e}\n"
                "Make sure your [firebase] section in Streamlit secrets has all required fields."
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Firebase from Streamlit secrets: {e}")

    # ── Fall back to local file ──────────────────────────────────────────────
    key_path = os.environ.get("FIREBASE_KEY_PATH", "firebase_key.json")
    if not os.path.exists(key_path):
        raise FileNotFoundError(
            f"Firebase key not found: '{key_path}'\n"
            "Locally: place firebase_key.json in the project folder.\n"
            "On Streamlit Cloud: add credentials under [firebase] in Secrets."
        )

    logger.info(f"Firebase: loaded from file {key_path}")
    return credentials.Certificate(key_path)


def _has_streamlit_secrets():
    """Check if Streamlit secrets exist and contain [firebase] section."""
    try:
        import streamlit as st
        return "firebase" in st.secrets
    except Exception:
        return False


def reset_client():
    global _db
    _db = None