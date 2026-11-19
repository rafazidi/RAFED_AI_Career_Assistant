from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: str = Field(default="auto", pattern="^(auto|fr|en)$")


class SourceItem(BaseModel):
    filename: str
    excerpt: str


class ProjectItem(BaseModel):
    name: str
    full_name: str
    description: str
    html_url: str
    language: str | None = None
    updated_at: str
    topics: list[str]


class ChatResponse(BaseModel):
    answer: str
    language: str
    sources: list[SourceItem] = []
    generation_enabled: bool
