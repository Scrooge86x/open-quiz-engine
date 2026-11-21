from src.config import MAX_NICK_LENGTH, MIN_NICK_LENGTH
from src.errors.validation import InvalidNickError


def validate_nick(raw_nick: str) -> str:
    trimmed_nick = raw_nick.strip()
    if len(trimmed_nick) < MIN_NICK_LENGTH or len(trimmed_nick) > MAX_NICK_LENGTH:
        raise InvalidNickError(
            f"Nick length must be between {MIN_NICK_LENGTH} and {MAX_NICK_LENGTH} characters."
        )

    if not trimmed_nick.isprintable():
        raise InvalidNickError("Nick must contain printable characters only.")

    return trimmed_nick
