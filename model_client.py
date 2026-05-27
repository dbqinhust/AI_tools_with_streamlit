import json
import os
from dataclasses import dataclass
from typing import Callable

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


DEFAULT_PROVIDER = "Gemini"
DEFAULT_MODELS = {
    "Gemini": "gemini-2.5-flash",
    "OpenAI": "gpt-4.1-mini",
}

load_dotenv()


class ClientConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ToolSpec:
    function: Callable
    openai_schema: dict


@st.cache_resource(show_spinner=False)
def _sdk_client(provider: str):
    if provider == "OpenAI":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ClientConfigurationError(
                "Add your `OPENAI_API_KEY` to the `.env` file to use OpenAI."
            )
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ClientConfigurationError(
                "Install dependencies from `requirements.txt` to use OpenAI."
            ) from error
        return OpenAI(api_key=api_key)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        raise ClientConfigurationError(
            "Add your `GEMINI_API_KEY` to the `.env` file to use Gemini."
        )
    return genai.Client(api_key=api_key)


class ModelClient:
    def __init__(self, provider: str = DEFAULT_PROVIDER, model: str | None = None):
        self.provider = provider
        self.model = model or DEFAULT_MODELS[provider]
        self.client = _sdk_client(provider)

    def complete(self, messages: list[dict], tools: list[ToolSpec] | None = None) -> str:
        tool_specs = tools or []
        if self.provider == "OpenAI":
            return self._complete_openai(messages, tool_specs)
        return self._complete_gemini(messages, tool_specs)

    def _complete_gemini(self, messages: list[dict], tools: list[ToolSpec]) -> str:
        contents = [
            types.Content(
                role="model" if message["role"] == "assistant" else "user",
                parts=[types.Part(text=message["content"])],
            )
            for message in messages
        ]
        config = None
        if tools:
            config = types.GenerateContentConfig(
                tools=[tool.function for tool in tools]
            )
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        return response.text or "No text response was returned."

    def _complete_openai(self, messages: list[dict], tools: list[ToolSpec]) -> str:
        schemas = [tool.openai_schema for tool in tools]
        registry = {tool.function.__name__: tool.function for tool in tools}
        input_items = list(messages)
        response = self.client.responses.create(
            model=self.model,
            input=input_items,
            tools=schemas,
        )

        for _ in range(5):
            input_items += response.output
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                return response.output_text or "No text response was returned."

            for call in calls:
                function = registry.get(call.name)
                result = (
                    function(**json.loads(call.arguments))
                    if function
                    else {"error": f"Unknown function: {call.name}"}
                )
                input_items.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.call_id,
                        "output": json.dumps(result),
                    }
                )

            response = self.client.responses.create(
                model=self.model,
                input=input_items,
                tools=schemas,
            )

        return "The tool workflow reached its maximum number of steps."


def provider_controls(scope: str) -> ModelClient | None:
    provider = st.sidebar.selectbox(
        "Provider",
        options=list(DEFAULT_MODELS),
        index=list(DEFAULT_MODELS).index(DEFAULT_PROVIDER),
        key=f"{scope}_provider",
    )
    model = st.sidebar.text_input(
        "Model",
        value=DEFAULT_MODELS[provider],
        key=f"{scope}_{provider.lower()}_model",
    )
    try:
        return ModelClient(provider=provider, model=model)
    except ClientConfigurationError as error:
        st.info(str(error))
        return None
