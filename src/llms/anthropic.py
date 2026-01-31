from openai import OpenAI

from src.config.config import DefaultConfig


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


if __name__ == "__main__":
    client = get_anthropic_client()
    response = get_anthropic_response(
        client,
        messages=[{"role": "user", "content": "你好"}],
        tools=[],
    )
    print(response)
