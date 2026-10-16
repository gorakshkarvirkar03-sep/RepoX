import streamlit as st
# Demo credentials for Hackathon testing/judges
DEMO_USERS = {
    "Student / Fresher": {"email": "student@repox.ai", "password": "password123", "name": "Alex (Student)"},
    "Recruiter": {"email": "recruiter@techcorp.com", "password": "password123", "name": "Sarah (TechCorp HR)"},
    "Admin": {"email": "admin@repox.ai", "password": "admin123", "name": "System Admin"}
}

def init_auth_state():
    """Initialize session state variables for authentication."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None

def logout():
    """Clear authentication state and log the user out."""
    st.session_state["authenticated"] = False
    st.session_state["user_role"] = None
    st.session_state["user_email"] = None
    st.session_state["user_name"] = None
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

    # Center the login card on the screen
    col1, col2, col3 = st.columns([1, 1.3, 1])

    with col2:
        with st.container(border=True):
            st.subheader("🔐 Portal Login")
            
            # Role Selector
            role = st.selectbox(
                "Select Your Role",
                ["Student / Fresher", "Recruiter", "Admin"]
            )

            tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

            # --- LOGIN TAB ---
            with tab_login:
                with st.form("login_form"):
                    email = st.text_input("Email Address", placeholder=DEMO_USERS[role]["email"])
                    password = st.text_input("Password", type="password", placeholder="••••••••")
                    submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)

                    if submit:
                        if not email or not password:
                            st.warning("Please enter both email and password.")
                        # Check Demo Credentials (or replace with Supabase check)
                        elif email == DEMO_USERS[role]["email"] and password == DEMO_USERS[role]["password"]:
                            st.session_state["authenticated"] = True
                            st.session_state["user_role"] = role
                            st.session_state["user_email"] = email
                            st.session_state["user_name"] = DEMO_USERS[role]["name"]
                            st.success(f"Welcome back, {DEMO_USERS[role]['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials for the selected role.")

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
                        
                        if role == "Recruiter":
                            company = st.text_input("Company Name", placeholder="Acme Inc.")
                        else:
                            github_handle = st.text_input("GitHub Username", placeholder="johndoe-dev")

                        new_pass = st.text_input("Create Password", type="password")
                        signup_submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

                        if signup_submit:
                            if not new_name or not new_email or not new_pass:
                                st.warning("Please fill in all fields.")
                            else:
                                # Auto-login after signup for smooth hackathon demo
                                st.session_state["authenticated"] = True
                                st.session_state["user_role"] = role
                                st.session_state["user_email"] = new_email
                                st.session_state["user_name"] = f"{new_name} ({role})"
                                if role == "Student / Fresher" and github_handle:
                                    st.session_state["username"] = github_handle
                                st.success("Account created successfully!")
                                st.rerun()