from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class Source(BaseModel):
    n: int
    source: str
    section: str
    page: int | None = None
    text: str
    rerank_score: float
    vector_rank: int


class AnswerResponse(BaseModel):
    answer: str
    found: bool
    sources: list[Source] = []


class SearchResult(BaseModel):
    source: str
    section: str
    page: int | None = None
    text: str
    vector_rank: int
    vector_score: float
    rerank_score: float


class HealthResponse(BaseModel):
    status: str
    chunks: int
    llm_enabled: bool