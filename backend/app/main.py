from contextlib import asynccontextmanager
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import ChatRequest, ChatResponse, ProjectItem, SourceItem
from app.services.github import GitHubAPIError, GitHubProject, github_projects
from app.services.llm import generate_answer, generation_is_configured
from app.services.rag import rag_service


_github_index_lock = Lock()
_github_index_signature: tuple[tuple[str, str, str, str, str], ...] | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    description="Bilingual RAG career assistant for Rafed Zidi.",
    version="0.1.0",
    lifespan=lifespan,
)

_allowed_origins = [
    origin.strip()
    for origin in settings.frontend_origin.split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[*_allowed_origins, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Rafed AI API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "indexed_chunks": rag_service._collection.count(),
        "generation_enabled": generation_is_configured(),
    }


def _sync_github_projects() -> list[GitHubProject]:
    global _github_index_signature

    with _github_index_lock:
        projects = github_projects.list_projects()
        signature = tuple(
            (
                project.full_name,
                project.updated_at,
                project.description,
                project.language or "",
                ",".join(project.topics),
            )
            for project in projects
        )
        if signature != _github_index_signature:
            documents = github_projects.knowledge_documents(projects)
            rag_service.replace_source_documents("github", documents)
            _github_index_signature = signature
        return projects


@app.get("/api/projects", response_model=list[ProjectItem])
def projects():
    try:
        current_projects = _sync_github_projects()
    except GitHubAPIError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return [project.to_dict() for project in current_projects]


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    matches = rag_service.search(request.message)
    context = "\n\n---\n\n".join(
        f"Source: {item['filename']}\n{item['text']}" for item in matches
    )
    answer = generate_answer(request.message, context, request.language)

    sources = [
        SourceItem(
            filename=item["filename"],
            excerpt=item["text"][:260] + ("…" if len(item["text"]) > 260 else ""),
        )
        for item in matches
    ]
    return ChatResponse(
        answer=answer,
        language=request.language,
        sources=sources,
        generation_enabled=generation_is_configured(),
    )
