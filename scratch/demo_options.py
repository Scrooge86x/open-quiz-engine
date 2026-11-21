import random

from src.config import QUESTION_TYPE_BOOLEAN, QUESTION_TYPE_MULTIPLE
from src.logic.option_shuffler import build_options


def main() -> None:
    incorrect_answers = ["Paris", "Berlin", "Rome"]
    original_incorrect = list(incorrect_answers)

    print("--- Multiple choice (seed 1, run 1) ---")
    options1, index1 = build_options(
        question_type=QUESTION_TYPE_MULTIPLE,
        correct_answer="London",
        incorrect_answers=incorrect_answers,
        rng=random.Random(1),
    )
    print(f"Options: {options1}, Index: {index1}")
    print(f"Selected option by index: {options1[index1]} (matches correct answer)")

    print("\n--- Multiple choice (seed 1, run 2 - identical output) ---")
    options2, index2 = build_options(
        question_type=QUESTION_TYPE_MULTIPLE,
        correct_answer="London",
        incorrect_answers=incorrect_answers,
        rng=random.Random(1),
    )
    print(f"Options: {options2}, Index: {index2}")

    print(
        f"\nInput incorrect_answers unchanged: {incorrect_answers == original_incorrect} "
        f"({incorrect_answers})"
    )

    print("\n--- Boolean question (correct answer: 'True') ---")
    bool_options_true, bool_index_true = build_options(
        question_type=QUESTION_TYPE_BOOLEAN,
        correct_answer="True",
        incorrect_answers=["False"],
        rng=random.Random(1),
    )
    print(f"Options: {bool_options_true}, Index: {bool_index_true}")

    print("\n--- Boolean question (correct answer: 'False') ---")
    bool_options_false, bool_index_false = build_options(
        question_type=QUESTION_TYPE_BOOLEAN,
        correct_answer="False",
        incorrect_answers=["True"],
        rng=random.Random(1),
    )
    print(f"Options: {bool_options_false}, Index: {bool_index_false}")


if __name__ == "__main__":
    main()
