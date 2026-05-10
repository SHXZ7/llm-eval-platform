import json

from app.models.schemas import GoldenTestCase


def load_dataset(path: str) -> list[GoldenTestCase]:

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    dataset = [
        GoldenTestCase(**item)
        for item in data
    ]

    return dataset
