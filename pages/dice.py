import streamlit as st

from model_client import provider_controls
from tools.handler import get_tool_specs


st.title("Roll Dice")
st.write("Ask the selected model to roll dice using the `roll_dice` tool.")

model_client = provider_controls("dice")
prompt = st.text_input(
    "Request",
    value="Roll two six-sided dice and tell me the total.",
)

if st.button("Roll", type="primary", disabled=model_client is None):
    with st.spinner("Rolling..."):
        try:
            reply = model_client.complete(
                [{"role": "user", "content": prompt}],
                tools=get_tool_specs("roll_dice"),
            )
            st.markdown(reply)
        except Exception as error:
            st.error(f"Model error: {error}")
