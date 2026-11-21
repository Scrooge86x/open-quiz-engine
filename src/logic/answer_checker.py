from src.errors.validation import InvalidOptionError


def is_answer_correct(selected_index: int, correct_index: int) -> bool:
    return selected_index == correct_index


def validate_option_index(selected_index: int, option_count: int) -> None:
    if not (0 <= selected_index < option_count):
        raise InvalidOptionError(
            f"Option index {selected_index} is out of bounds (0..{option_count - 1})."
        )
