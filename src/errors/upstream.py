from src.errors.base import QuizError


class UpstreamRateLimitedError(QuizError):
    error_code: str = "upstream_rate_limited"
    default_message: str = "Upstream trivia service is rate limited. Please try again later."


class UpstreamUnavailableError(QuizError):
    error_code: str = "upstream_unavailable"
    default_message: str = "Upstream trivia service is currently unavailable."
