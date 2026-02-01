from openai import OpenAI

from src.config.config import DefaultConfig
from src.llms.cache import get_response_with_cache


def get_anthropic_client(
    base_url=DefaultConfig.anthropic_base_url,
    api_key=DefaultConfig.anthropic_api_key,
    **kwargs,
):
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        **kwargs,
    )
    return client


def get_anthropic_response(
    client,
    messages: list,
    tools: list,
    model_name: str = DefaultConfig.anthropic_reasoning_model,
    **kwargs,
):
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        **kwargs,
    )
    return response


def get_anthropic_response_with_cache(
    client,
    messages: list,
    tools: list,
    invoke=get_anthropic_response,
    cache_path: str = ".cache/anthropic/",
    **kwargs,
):
    response = get_response_with_cache(
        client,
        invoke,
        messages=messages,
        tools=tools,
        cache_path=cache_path,
        **kwargs,
    )
    return response


if __name__ == "__main__":
    client = get_anthropic_client()
    # response = get_anthropic_response(
    #     client,
    #     messages=[{"role": "user", "content": "你好"}],
    #     tools=[],
    # )
    # print(response)
    response = get_anthropic_response_with_cache(
        client,
        messages=[{"role": "user", "content": "你好"}],
        tools=[],
    )
    print(response)
