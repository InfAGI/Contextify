import hashlib
import json
import os
from openai.types.chat.chat_completion import ChatCompletion


def get_response_with_cache(
    client,
    invoke,
    messages: list,
    tools: list,
    cache_path: str = ".cache/",
    **kwargs,
):
    cache_key = hashlib.md5(f"_{messages}_{tools}".encode()).hexdigest()
    if cache_path:
        try:
            with open(f"{cache_path}/{cache_key}", "r") as f:
                response = json.load(f)
                response = ChatCompletion(**response)
                return response
        except Exception:
            pass

    response = invoke(client=client, messages=messages, tools=tools, **kwargs)
    if cache_path:
        os.makedirs(cache_path, exist_ok=True)
        with open(f"{cache_path}/{cache_key}", "w") as f:
            json.dump(response.model_dump(), f, indent=4)

    return response


if __name__ == "__main__":
    from src.llms.anthropic import get_anthropic_client, get_anthropic_response

    client = get_anthropic_client()
    response = get_response_with_cache(
        client,
        invoke=get_anthropic_response,
        messages=[{"role": "user", "content": "你好"}],
        tools=[],
    )
    print(response)
