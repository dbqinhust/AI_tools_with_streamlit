import streamlit as st

from model_client import provider_controls, show_tool_calls
from tools.handler import get_tool_specs


st.title("Roll Dice")
st.write("Ask the selected model to roll dice using the `roll_dice` tool.")

model_client = provider_controls("dice")
prompt = st.text_input(
    "Request",
    value="Roll two six-sided dice and tell me the total.",
)

if "dice_response" in st.session_state:
    st.markdown(st.session_state.dice_response["content"])
    show_tool_calls(st.session_state.dice_response["tool_calls"])

if st.button("Roll", type="primary", disabled=model_client is None):
    with st.spinner("Rolling..."):
        try:
            response = model_client.complete(
                [{"role": "user", "content": prompt}],
                tools=get_tool_specs("roll_dice"),
            )
            st.session_state.dice_response = {
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
            st.rerun()
        except Exception as error:
            st.error(f"Model error: {error}")
