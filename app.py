import streamlit as st


st.set_page_config(page_title="AI Tool Demos", page_icon=":speech_balloon:")

pages = [
    st.Page("pages/dice.py", title="Roll Dice", icon=":material/casino:"),
    st.Page("pages/memory_search.py", title="Memory Agent", icon=":material/memory:"),
    st.Page("pages/retrieval_chat.py", title="Retrieval Chat", icon=":material/chat:"),
]

st.navigation(pages).run()
