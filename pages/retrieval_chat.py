import streamlit as st

from model_client import provider_controls
from tools.handler import get_tool_specs


st.title("Retrieval Chat")
st.caption("The assistant answers support questions using `data/help_center_faq.json`.")

model_client = provider_controls("retrieval_chat")
if "retrieval_messages" not in st.session_state:
    st.session_state.retrieval_messages = []

for message in st.session_state.retrieval_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a help-center question, such as: What is the refund policy?"):
    st.session_state.retrieval_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model_client is None:
            st.error("Configure a provider API key to send messages.")
        else:
            try:
                reply = model_client.complete(
                    st.session_state.retrieval_messages,
                    tools=get_tool_specs("search_help_center"),
                )
                st.markdown(reply)
                st.session_state.retrieval_messages.append(
                    {"role": "assistant", "content": reply}
                )
            except Exception as error:
                st.error(f"Model error: {error}")
