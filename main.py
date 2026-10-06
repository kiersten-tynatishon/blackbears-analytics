import streamlit as st

st.set_page_config(
    page_title="Black Bears Analytics Hub",
    page_icon="🏒",
    layout="wide"
)

st.title("Binghamton Black Bears Analytics Portal")
st.markdown("### Welcome! Select a module below to begin.")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Shot & Opponent Analytics")
    st.write(
        "Analyze team scoring locations, goal probabilities, and opponent shot tendencies "
        "across all games."
    )
    if st.button("Go to Shot Map & Analytics", use_container_width=True):
        st.switch_page("pages/1_Shot_Analytics.py")

with col2:
    st.subheader("5-Player Line Evaluator")
    st.write(
        "Evaluate 5-player line combinations (3 Forwards, 2 Defensemen) for offensive "
        "generation, shot suppression, and high-danger chance control."
    )
    if st.button("Go to Line Evaluator", use_container_width=True):
        st.switch_page("pages/2_Line_Builder.py")

st.markdown("---")
st.info("💡 **Tip:** You can also use the navigation menu on the left sidebar to switch between views anytime.")