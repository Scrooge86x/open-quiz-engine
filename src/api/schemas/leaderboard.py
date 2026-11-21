from pydantic import BaseModel, ConfigDict


class LeaderboardEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rank: int
    nick: str
    score: int
    duration_seconds: float
