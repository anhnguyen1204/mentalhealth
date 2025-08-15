import streamlit as st
from src.authentication import login, register, guest_login
import src.sidebar as sidebar

def main():
    sidebar.show_sidebar()
    
    # Log-in Interface
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        with st.expander('MENTAL HEALTH', expanded=True):
            login_tab, create_tab, guest_tab = st.tabs(
                [
                    "Log in",
                    "Sign Up",
                    "Guest"
                ]
            )
            with create_tab:
                register()
            with login_tab:
                login()
            with guest_tab:
                guest_login()
    else:
        
        col1, col2 = st.columns(2)
        with col1:
            st.image("data/images/chat.jpeg")
            if st.button("Talk to AI expert"):
                st.switch_page("pages/chat.py")
        with col2:
            st.image("data/images/chart.jpeg")
            if st.button("Track your mental health information"):
                st.switch_page("pages/user.py")
        st.success(f'Welcom {st.session_state.username}, Let\'s explore features of mental health care app!', icon="🎉")
if __name__ == "__main__":
    main()