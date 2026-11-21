import random

from src.config import BOOLEAN_OPTIONS, QUESTION_TYPE_BOOLEAN


def build_options(
    question_type: str,
    correct_answer: str,
    incorrect_answers: list[str],
    rng: random.Random,
) -> tuple[list[str], int]:
    if question_type == QUESTION_TYPE_BOOLEAN:
        options = list(BOOLEAN_OPTIONS)
        return options, options.index(correct_answer)

    options = [correct_answer, *incorrect_answers]
    rng.shuffle(options)
    return options, options.index(correct_answer)
