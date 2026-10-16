import streamlit as st
from modules.db import create_user, verify_user, link_github

# Demo credentials for Hackathon testing/judges (not stored in database)
DEMO_USERS = {
    "Student / Fresher": {"email": "student@repox.ai", "password": "password123", "name": "Alex (Student)"},
    "Recruiter": {"email": "recruiter@techcorp.com", "password": "password123", "name": "Sarah (TechCorp HR)"},
    "Admin": {"email": "admin@repox.ai", "password": "admin123", "name": "System Admin"}
}


def init_auth_state():
    """Initialize session state variables for authentication."""
    defaults = {
        "authenticated": False,
        "user_role": None,
        "user_email": None,
        "user_name": None,
        "user_id": None,
        "repox_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _start_session(user, role):
    """Fill the session from a database user."""
    st.session_state["authenticated"] = True
    st.session_state["user_role"] = role
    st.session_state["user_email"] = user["email"]
    st.session_state["user_name"] = user["full_name"]
    st.session_state["user_id"] = user["id"]
    st.session_state["repox_id"] = user["repox_id"]
    st.session_state["recruiter_consent"] = user.get("recruiter_consent", False)
    if user.get("github_username"):
        st.session_state["username"] = user["github_username"]


def logout():
    """Clear authentication state and log the user out."""
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None
    st.session_state["user_id"] = None
    st.session_state["repox_id"] = None
    st.session_state["repos"] = []
    st.session_state["username"] = ""
    st.rerun()


def login_page():
    """Render the login and sign-up UI."""
    st.markdown("""
    <div class="hero">
        <h1>Welcome to RepoX 🚀</h1>
        <p>Transform your GitHub projects into career opportunities with AI.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.3, 1])

    with col2:
        with st.container(border=True):
            st.subheader("🔐 Portal Login")

            role = st.selectbox(
                "Select Your Role",
                ["Student / Fresher", "Recruiter", "Admin"]
            )

            tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

            # --- LOGIN TAB ---
            with tab_login:
                with st.form("login_form"):
                    email = st.text_input("Email Address", placeholder="you@example.com")
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                    if submit:
                        if not email or not password:
                            st.warning("Please enter both email and password.")
                        else:
                            try:
                                user, err = verify_user(email, password)
                            except Exception as e:
                                user, err = None, f"Database error: {e}"

                            if user:
                                if user.get("role") != role:
                                    st.error(f"This account is registered as '{user.get('role')}'. Please select that role.")
                                else:
                                    _start_session(user, role)
                                    st.rerun()
                            # Fallback: demo accounts (not in database)
                            elif (email.strip().lower() == DEMO_USERS[role]["email"]
                                  and password == DEMO_USERS[role]["password"]):
                                st.session_state["authenticated"] = True
                                st.session_state["user_role"] = role
                                st.session_state["user_email"] = DEMO_USERS[role]["email"]
                                st.session_state["user_name"] = DEMO_USERS[role]["name"]
                                st.rerun()
                            else:
                                st.error(err or "Invalid credentials.")

                # Hackathon Quick-Login Helper for Judges
                st.divider()
                st.caption("⚡ **Hackathon Demo Mode (1-Click Login):**")
                if st.button(f"Demo Login as {role}", use_container_width=True):
                    st.session_state["authenticated"] = True
                    st.session_state["user_role"] = role
                    st.session_state["user_email"] = DEMO_USERS[role]["email"]
                    st.session_state["user_name"] = DEMO_USERS[role]["name"]
                    st.rerun()

            # --- SIGN UP TAB ---
            with tab_signup:
                if role == "Admin":
                    st.info("🔒 Admin accounts cannot be registered publicly. Contact system administrator.")
                else:
                    with st.form("signup_form"):
                        new_name = st.text_input("Full Name", placeholder="John Doe")
                        new_email = st.text_input("Email Address", placeholder="you@example.com")

                        github_handle = ""
                        if role == "Recruiter":
                            st.text_input("Company Name", placeholder="Acme Inc.")
                        else:
                            github_handle = st.text_input("GitHub Username", placeholder="johndoe-dev")

                        new_pass = st.text_input("Create Password (min 6 characters)", type="password")
                        signup_submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                        if signup_submit:
                            if not new_name or not new_email or not new_pass:
                                st.warning("Please fill in all fields.")
                            elif len(new_pass) < 6:
                                st.warning("Password must be at least 6 characters.")
                            else:
                                try:
                                    user, err = create_user(new_name, new_email, new_pass, role)
                                except Exception as e:
                                    user, err = None, f"Database error: {e}"

                                if err:
                                    st.error(err)
                                else:
                                    if github_handle.strip():
                                        link_github(user["id"], github_handle.strip())
                                        user["github_username"] = github_handle.strip()
                                    _start_session(user, role)
                                    st.rerun()