import argparse
from pathlib import Path

from app.config import settings
from app.services.rag import load_knowledge_documents, rag_service


def main() -> None:
    parser = argparse.ArgumentParser(description="Index Rafed AI profile documents.")
    parser.add_argument("--app-dir", default="backend", help="Kept for the README command.")
    parser.parse_args()

    folder = settings.absolute_knowledge_base_dir
    documents = load_knowledge_documents(folder)
    if not documents:
        print(f"No Markdown documents found in: {folder}")
        return

    count = rag_service.index_documents(documents)
    print(f"Indexed {count} chunks from {folder}")


if __name__ == "__main__":
    main()
