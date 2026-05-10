from app.llm.client import client


async def judge_summary(
    email: str,
    expected_summary: str,
    predicted_summary: str,
    model: str = "llama-3.3-70b-versatile"
):

    prompt = f"""
    You are evaluating summary quality.

    Email:
    {email}

    Expected Summary:
    {expected_summary}

    Predicted Summary:
    {predicted_summary}

    Rate the predicted summary from 1 to 5.

    1 = very poor
    5 = excellent

    Return ONLY a number.
    """

    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    score = int(
        response.choices[0]
        .message.content.strip()
    )

    return score
