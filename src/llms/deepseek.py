import os
import json
import hashlib
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

from src.config.config import DefaultConfig


def get_deepseek_client(
    base_url=DefaultConfig.deepseek_base_url,
    api_key=DefaultConfig.deepseek_api_key,
    **kwargs,
):
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        **kwargs,
    )
    return client


def get_deepseek_response(
    client,
    messages: list,
    tools: list,
    extra_body={"thinking": {"type": "enabled"}},
    model_name: str = DefaultConfig.deepseek_reasoning_model,
    **kwargs,
):
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        extra_body=extra_body,
        **kwargs,
    )
    return response


def get_deepseek_response_with_cache(
    client,
    messages: list,
    tools: list,
    extra_body={"thinking": {"type": "enabled"}},
    model_name: str = DefaultConfig.deepseek_reasoning_model,
    cache_path: str = ".cache/deepseek",
    **kwargs,
):
    cache_key = hashlib.md5(f"{model_name}_{messages}_{tools}".encode()).hexdigest()
    if cache_path:
        try:
            with open(f"{cache_path}/{cache_key}", "r") as f:
                response = json.load(f)
                response = ChatCompletion(**response)
                return response
        except Exception as e:
            pass

    response = get_deepseek_response(
        client,
        messages,
        tools,
        extra_body,
        model_name,
        **kwargs,
    )
    if cache_path:
        os.makedirs(cache_path, exist_ok=True)
        with open(f"{cache_path}/{cache_key}", "w") as f:
            json.dump(response.model_dump(), f)
    return response


if __name__ == "__main__":
    client = get_deepseek_client()
    response = get_deepseek_response(
        client,
        messages=[{"role": "user", "content": "你好"}],
        tools=[],
    )
    # response = get_deepseek_response_with_cache(
    #     client,
    #     messages=[{"role": "user", "content": "你好"}],
    #     tools=[],
    # )
    print(response)
