import streamlit as st

from model_client import provider_controls
from tools.handler import get_tool_specs
from tools.read_from_memory import read_from_memory


st.title("Memory Agent")
st.caption("Ask the assistant to remember information, or ask what it remembers.")

stored_memories = read_from_memory()
st.subheader("Saved Memories")
if stored_memories["status"] == "success":
    st.text(stored_memories["memories"])
else:
    st.error(stored_memories["message"])

model_client = provider_controls("memory_agent")
if "memory_messages" not in st.session_state:
    st.session_state.memory_messages = []

for message in st.session_state.memory_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("For example: Remember that my preferred size is medium."):
    st.session_state.memory_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model_client is None:
            st.error("Configure a provider API key to send messages.")
        else:
            try:
                reply = model_client.complete(
                    st.session_state.memory_messages,
                    tools=get_tool_specs("read_from_memory", "write_to_memory"),
                )
                st.markdown(reply)
                st.session_state.memory_messages.append(
                    {"role": "assistant", "content": reply}
                )
            except Exception as error:
                st.error(f"Model error: {error}")
