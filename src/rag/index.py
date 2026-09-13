import os
from pathlib import Path

import faiss
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

KB_DIR = Path("knowledge_base")
INDEX_DIR = Path(os.getenv("RAG_INDEX_DIR", "data/faiss_index"))


def load_documents():
    documents = []

    for file_path in sorted(KB_DIR.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")

        if text.strip():
            documents.append(
                {
                    "content": text,
                    "source": file_path.name,
                }
            )

    if not documents:
        raise RuntimeError("No knowledge base documents were found.")

    return documents


def build_index():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is required to build the FAISS index."
        )

    if not KB_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {KB_DIR}"
        )

    documents = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )

    chunks = []

    for document in documents:
        split_texts = splitter.split_text(document["content"])

        for text in split_texts:
            chunks.append(
                {
                    "content": text,
                    "source": document["source"],
                }
            )

    embeddings_model = OpenAIEmbeddings(
        model=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        )
    )

    texts = [chunk["content"] for chunk in chunks]

    embeddings = embeddings_model.embed_documents(texts)

    dimension = len(embeddings[0])

    index = faiss.IndexFlatL2(dimension)

    index.add(
        __import__("numpy").array(
            embeddings,
            dtype="float32",
        )
    )

    INDEX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    faiss.write_index(
        index,
        str(INDEX_DIR / "index.faiss"),
    )

    import json

    with open(
        INDEX_DIR / "metadata.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "embedding_dimension": dimension,
        "index": str(INDEX_DIR),
    }


if __name__ == "__main__":
    print(build_index())