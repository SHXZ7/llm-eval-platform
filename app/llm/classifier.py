import json
import re
import yaml
import time
from app.llm.client import client
from app.models.schemas import (
    ClassificationResponse,
    ClassificationResult,
    PromptConfig,
)


def load_prompt(prompt_path: str) -> PromptConfig:
    with open(prompt_path, "r") as file:
        data = yaml.safe_load(file)

    return PromptConfig(**data)


def clean_json_response(text: str) -> str:
    text = text.strip()

    text = re.sub(r"^```json", "", text)
    text = re.sub(r"```$", "", text)

    return text.strip()


async def classify_email(
    email: str,
    prompt_config: PromptConfig,
) -> ClassificationResponse:

    messages = [
        {
            "role": "system",
            "content": prompt_config.system_prompt,
        }
    ]

    for example in prompt_config.few_shot_examples:
        messages.append(
            {
                "role": "user",
                "content": example.input,
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": example.output,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": email,
        }
    )

    start_time = time.perf_counter()

    response = await client.chat.completions.create(
        model=prompt_config.model,
        messages=messages,
        temperature=prompt_config.temperature,
        max_tokens=prompt_config.max_tokens,
    )

    end_time = time.perf_counter()

    latency_ms = (
        end_time - start_time
    ) * 1000

    usage = response.usage

    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    raw_output = response.choices[0].message.content

    cleaned_output = clean_json_response(raw_output)

    try:

        parsed_output = json.loads(
            cleaned_output
        )

        result = ClassificationResult(
            **parsed_output
        )

    except Exception as e:

        print(
            f"Failed to parse model output: {e}"
        )

        result = ClassificationResult(
            category="general",
            summary="Parsing failure."
        )

    return ClassificationResponse(

        result=result,

        latency_ms=latency_ms,

        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,

        raw_response=response.model_dump()
    )