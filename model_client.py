import json
import os
from dataclasses import dataclass
from functools import wraps
from inspect import signature
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


@dataclass(frozen=True)
class ToolCallInfo:
    function_name: str
    function_args: dict
    result: object


@dataclass(frozen=True)
class CompletionResult:
    content: str
    tool_calls: list[ToolCallInfo]


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

    def complete(
        self, messages: list[dict], tools: list[ToolSpec] | None = None
    ) -> CompletionResult:
        tool_specs = tools or []
        if self.provider == "OpenAI":
            return self._complete_openai(messages, tool_specs)
        return self._complete_gemini(messages, tool_specs)

    def _complete_gemini(
        self, messages: list[dict], tools: list[ToolSpec]
    ) -> CompletionResult:
        contents = [
            types.Content(
                role="model" if message["role"] == "assistant" else "user",
                parts=[types.Part(text=message["content"])],
            )
            for message in messages
        ]
        config = None
        tool_calls = []
        if tools:
            tracked_functions = []
            for tool in tools:
                function = tool.function

                @wraps(function)
                def tracked_function(*args, _function=function, **kwargs):
                    function_args = dict(
                        signature(_function).bind_partial(*args, **kwargs).arguments
                    )
                    result = _function(*args, **kwargs)
                    tool_calls.append(
                        ToolCallInfo(
                            function_name=_function.__name__,
                            function_args=function_args,
                            result=result,
                        )
                    )
                    return result

                tracked_functions.append(tracked_function)

            config = types.GenerateContentConfig(
                tools=tracked_functions
            )
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        return CompletionResult(
            content=response.text or "No text response was returned.",
            tool_calls=tool_calls,
        )

    def _complete_openai(
        self, messages: list[dict], tools: list[ToolSpec]
    ) -> CompletionResult:
        schemas = [tool.openai_schema for tool in tools]
        registry = {tool.function.__name__: tool.function for tool in tools}
        input_items = [
            {"role": message["role"], "content": message["content"]}
            for message in messages
        ]
        tool_calls = []
        response = self.client.responses.create(
            model=self.model,
            input=input_items,
            tools=schemas,
        )

        for _ in range(5):
            input_items += response.output
            calls = [item for item in response.output if item.type == "function_call"]
            if not calls:
                return CompletionResult(
                    content=response.output_text or "No text response was returned.",
                    tool_calls=tool_calls,
                )

            for call in calls:
                function = registry.get(call.name)
                function_args = json.loads(call.arguments)
                result = (
                    function(**function_args)
                    if function
                    else {"error": f"Unknown function: {call.name}"}
                )
                tool_calls.append(
                    ToolCallInfo(
                        function_name=call.name,
                        function_args=function_args,
                        result=result,
                    )
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

        return CompletionResult(
            content="The tool workflow reached its maximum number of steps.",
            tool_calls=tool_calls,
        )


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


def show_tool_calls(tool_calls: list[dict] | list[ToolCallInfo]) -> None:
    for tool_call in tool_calls:
        if isinstance(tool_call, ToolCallInfo):
            tool_call_info = {
                "function_name": tool_call.function_name,
                "function_args": tool_call.function_args,
                "result": tool_call.result,
            }
        else:
            tool_call_info = tool_call

        st.markdown(f"🔧 **Tool Executed:** `{tool_call_info['function_name']}`")
        st.markdown("**Input:**")
        st.code(json.dumps(tool_call_info["function_args"], indent=2), language="json")
        st.markdown("**Output:**")
        st.code(json.dumps(tool_call_info["result"], indent=2), language="json")
