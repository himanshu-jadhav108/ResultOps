"""
Authentication module for ResultOps - Feature-level access control.
Three tiers: READ, WRITE, ADMIN (each with a separate password hash).
"""

import hashlib
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


class AuthManager:
    """Manages feature-level authentication with session state persistence."""

    def __init__(self):
        self._load_hashes()
        self._init_state()

    def _load_hashes(self):
        self.read_hash  = os.getenv("READ_PASSWORD_HASH", "")
        self.write_hash = os.getenv("WRITE_PASSWORD_HASH", "")
        self.admin_hash = os.getenv("ADMIN_PASSWORD_HASH", "")

    def _init_state(self):
        for key in ("read_authenticated", "write_authenticated", "admin_authenticated", "auth_error"):
            if key not in st.session_state:
                st.session_state[key] = False if key != "auth_error" else None

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    # ── Verify ────────────────────────────────────────────────────────────────
    def _verify(self, password: str, expected_hash: str) -> bool:
        if not expected_hash:
            return False
        return self.hash_password(password) == expected_hash

    # ── Authenticate (sets session state) ─────────────────────────────────────
    def authenticate_read(self, password: str) -> bool:
        if self._verify(password, self.read_hash):
            st.session_state.read_authenticated = True
            st.session_state.auth_error = None
            return True
        st.session_state.auth_error = "Invalid READ password"
        return False

    def authenticate_write(self, password: str) -> bool:
        if self._verify(password, self.write_hash):
            st.session_state.write_authenticated = True
            st.session_state.auth_error = None
            return True
        st.session_state.auth_error = "Invalid WRITE password"
        return False

    def authenticate_admin(self, password: str) -> bool:
        if self._verify(password, self.admin_hash):
            st.session_state.admin_authenticated = True
            st.session_state.auth_error = None
            return True
        st.session_state.auth_error = "Invalid ADMIN password"
        return False

    # ── Status properties ─────────────────────────────────────────────────────
    @property
    def is_read_authenticated(self) -> bool:
        return st.session_state.get("read_authenticated", False)

    @property
    def is_write_authenticated(self) -> bool:
        return st.session_state.get("write_authenticated", False)

    @property
    def is_admin_authenticated(self) -> bool:
        return st.session_state.get("admin_authenticated", False)

    # ── Logout ────────────────────────────────────────────────────────────────
    def reset_authentication(self):
        for k in ("read_authenticated", "write_authenticated", "admin_authenticated", "auth_error"):
            st.session_state[k] = False if k != "auth_error" else None

    def logout(self):
        self.reset_authentication()
        st.rerun()

    def render_logout_button(self):
        if self.is_read_authenticated or self.is_write_authenticated or self.is_admin_authenticated:
            if st.sidebar.button("🚪 Logout", type="secondary", use_container_width=True):
                self.logout()

    # ── Gate helpers (render login UI if not authenticated) ────────────────────
    def require_read_auth(self, show_ui: bool = True) -> bool:
        if self.is_read_authenticated:
            return True
        if show_ui:
            st.markdown("## 🔐 Protected Area")
            st.warning("This section requires **READ** authentication.")
            pw = st.text_input("READ Password", type="password", key="read_pw_input")
            if st.button("Authenticate", type="primary", key="read_auth_btn"):
                if self.authenticate_read(pw):
                    st.success("✅ READ access granted!")
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
                    st.stop()
            else:
                st.stop()
        return False

    def require_write_auth(self, show_ui: bool = True) -> bool:
        if self.is_write_authenticated:
            return True
        if show_ui:
            with st.container():
                st.info("🔐 **WRITE Authentication Required**")
                st.write("Enter WRITE password to save data to database.")
                pw = st.text_input("WRITE Password", type="password", key="write_pw_input")
                c1, c2 = st.columns([1, 3])
                with c1:
                    if st.button("Authenticate", type="primary", key="write_auth_btn"):
                        if self.authenticate_write(pw):
                            st.success("✅ WRITE access granted!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid password")
        return False

    def require_admin_auth(self, show_ui: bool = True) -> bool:
        """Gate for admin-only sections (System Stats, deletions)."""
        if self.is_admin_authenticated:
            return True
        if show_ui:
            st.markdown("## 🔒 Admin Access Required")
            st.warning("This section requires **ADMIN** authentication.")
            pw = st.text_input("Admin Password", type="password", key="admin_pw_input")
            if st.button("Authenticate as Admin", type="primary", key="admin_auth_btn"):
                if self.authenticate_admin(pw):
                    st.success("✅ Admin access granted!")
                    st.rerun()
                else:
                    st.error("❌ Invalid admin password")
                    st.stop()
            else:
                st.stop()
        return False


# Global instance
auth_manager = AuthManager()

# Convenience functions
def hash_password(password: str) -> str:
    return AuthManager.hash_password(password)