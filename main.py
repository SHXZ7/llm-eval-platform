import asyncio
import json
from datetime import datetime

from app.llm.classifier import classify_email, load_prompt
from app.evals.dataset_loader import load_dataset
from app.evals.runner import run_evaluation
    
async def main() -> None:
    prompt_config = load_prompt(
        "app/llm/prompts/v1.yaml"
    )

    dataset = load_dataset(
        "data/golden_dataset_small.json"
    )

    print(dataset[0])

    results = await run_evaluation(
        dataset=dataset,
        prompt_config=prompt_config
    )

    print(results[0])

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        f"outputs/eval_runs/"
        f"eval_{timestamp}.json"
    )

    with open(output_path, "w") as f:
        json.dump(
            [
                result.model_dump()
                for result in results
            ],
            f,
            indent=2
        )

    email = """
    Hi team,

    I was charged twice for my subscription this month.
    Can someone help me get a refund?

    Thanks,
    Sarah
    """

    result = await classify_email(
        email=email,
        prompt_config=prompt_config,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())