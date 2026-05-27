import streamlit as st

from model_client import provider_controls, show_tool_calls
from tools.handler import get_tool_specs
from tools.read_from_memory import read_from_memory


st.title("Memory Agent")
st.caption("Ask the assistant to remember information, or ask what it remembers.")

model_client = provider_controls("memory_agent")
if "memory_messages" not in st.session_state:
    st.session_state.memory_messages = []

for message in st.session_state.memory_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        show_tool_calls(message.get("tool_calls", []))

if prompt := st.chat_input("For example: Remember that my preferred size is medium."):
    st.session_state.memory_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if model_client is None:
            st.error("Configure a provider API key to send messages.")
        else:
            try:
                response = model_client.complete(
                    st.session_state.memory_messages,
                    tools=get_tool_specs("read_from_memory", "write_to_memory"),
                )
                st.markdown(response.content)
                show_tool_calls(response.tool_calls)
                st.session_state.memory_messages.append(
                    {
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [
                            {
                                "function_name": tool_call.function_name,
                                "function_args": tool_call.function_args,
                                "result": tool_call.result,
                            }
                            for tool_call in response.tool_calls
                        ],
                    }
                )
            except Exception as error:
                st.error(f"Model error: {error}")
