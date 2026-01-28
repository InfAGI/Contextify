from openai import OpenAI

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


if __name__ == "__main__":
    client = get_deepseek_client()
    response = get_deepseek_response(
        client,
        messages=[{"role": "user", "content": "你好"}],
        tools=[],
    )
    print(response)
