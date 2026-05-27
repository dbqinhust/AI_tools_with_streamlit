import streamlit as st

from model_client import provider_controls


st.title("Chatbot")

model_client = provider_controls("chatbot")
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model_client is None:
            st.error("Configure a provider API key to send messages.")
        else:
            try:
                assistant_reply = model_client.complete(st.session_state.messages)
                st.markdown(assistant_reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_reply}
                )
            except Exception as error:
                st.error(f"Model error: {error}")
