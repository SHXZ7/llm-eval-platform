from typing import List, Literal
from pydantic import BaseModel


class FewShotExample(BaseModel):
    input: str
    output: str


class PromptConfig(BaseModel):
    version: str
    created_at: str
    model: str
    description: str
    system_prompt: str
    few_shot_examples: List[FewShotExample]
    temperature: float
    max_tokens: int


class ClassificationResult(BaseModel):
    category: Literal[
        "billing",
        "technical",
        "account",
        "general"
    ]
    summary: str


class EvalResult(BaseModel):

    case_id: str

    expected_category: str
    predicted_category: str

    expected_summary: str
    predicted_summary: str

    category_correct: bool

    summary_score: int

    latency_ms: float

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    difficulty: str

    raw_output: dict


class GoldenTestCase(BaseModel):
    id: str
    email: str
    expected_category: Literal[
        "billing",
        "technical",
        "account",
        "general"
    ]
    expected_summary: str
    difficulty: Literal[
        "easy",
        "medium",
        "hard"
    ]
    notes: str

class ClassificationResponse(BaseModel):

    result: ClassificationResult

    latency_ms: float

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    raw_response: dict