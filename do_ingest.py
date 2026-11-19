import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.config import settings
from app.services.rag import load_knowledge_documents, rag_service

folder = settings.absolute_knowledge_base_dir
documents = load_knowledge_documents(folder)
print(f"Found {len(documents)} documents")
if documents:
    count = rag_service.index_documents(documents)
    print(f"Indexed {count} chunks")
else:
    print("No documents found")
print("Done")