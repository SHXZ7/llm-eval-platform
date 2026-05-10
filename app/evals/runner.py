import asyncio

from openai import RateLimitError

from app.llm.classifier import classify_email
from app.evals.judge import judge_summary
from app.models.schemas import EvalResult


async def evaluate_single_case(
    test_case,
    prompt_config,
    semaphore: asyncio.Semaphore,
    max_retries: int,
    request_delay: float,
):

    async with semaphore:
        for attempt in range(max_retries + 1):
            try:
                prediction = await classify_email(
                    email=test_case.email,
                    prompt_config=prompt_config
                )

                summary_score = await judge_summary(
                    email=test_case.email,
                    expected_summary=test_case.expected_summary,
                    predicted_summary=prediction.result.summary
                )

                await asyncio.sleep(request_delay)
                break
            except RateLimitError:
                if attempt >= max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)

    return EvalResult(
        case_id=test_case.id,

        expected_category=test_case.expected_category,
        predicted_category=prediction.result.category,

        expected_summary=test_case.expected_summary,
        predicted_summary=prediction.result.summary,

        category_correct=(
            prediction.result.category ==
            test_case.expected_category
        ),

        summary_score=summary_score,

        latency_ms=prediction.latency_ms,

        prompt_tokens=prediction.prompt_tokens,
        completion_tokens=prediction.completion_tokens,
        total_tokens=prediction.total_tokens,

        difficulty=test_case.difficulty,

        raw_output=prediction.raw_response
    )


async def run_evaluation(
    dataset,
    prompt_config,
    max_concurrency: int = 1,
    max_retries: int = 3,
    request_delay: float = 2.1,
):

    semaphore = asyncio.Semaphore(max_concurrency)

    tasks = [
        evaluate_single_case(
            test_case,
            prompt_config,
            semaphore,
            max_retries,
            request_delay,
        )
        for test_case in dataset
    ]

    results = await asyncio.gather(*tasks)

    return results