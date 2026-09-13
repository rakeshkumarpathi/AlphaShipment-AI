import json
import os
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()

INDEX_DIR = Path(
    os.getenv("RAG_INDEX_DIR", "data/faiss_index")
)


def load_index():
    index_path = INDEX_DIR / "index.faiss"
    metadata_path = INDEX_DIR / "metadata.json"

    if not index_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {INDEX_DIR}. "
            "Run: python -m src.rag.index"
        )

    index = faiss.read_index(str(index_path))

    with open(
        metadata_path,
        "r",
        encoding="utf-8",
    ) as file:
        metadata = json.load(file)

    return index, metadata


def retrieve(query: str, k: int | None = None):
    index, metadata = load_index()

    if k is None:
        k = int(os.getenv("RAG_TOP_K", "4"))

    embeddings_model = OpenAIEmbeddings(
        model=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        )
    )

    query_embedding = embeddings_model.embed_query(query)

    query_vector = np.array(
        [query_embedding],
        dtype="float32",
    )

    distances, indices = index.search(
        query_vector,
        k,
    )

    results = []

    for distance, index_position in zip(
        distances[0],
        indices[0],
    ):
        if index_position == -1:
            continue

        item = metadata[index_position]

        results.append(
            {
                "content": item["content"],
                "source": item["source"],
                "distance": float(distance),
            }
        )
    return results

def build_shipment_query(shipment, exception_result):
    return f"""
            Shipment exception analysis:

            Status: {shipment.get("status", "Not provided")}
            Priority: {shipment.get("priority", "Not provided")}
            Delay hours: {shipment.get("delay_hours", "Not provided")}
            Reason: {shipment.get("reason", "Not provided")}
            Customs status: {shipment.get("customs_status", "Not provided")}
            Weather condition: {shipment.get("weather_condition", "Not provided")}
            Port congestion: {shipment.get("port_congestion", "Not provided")}

            Deterministic exception:
            Exception: {exception_result.get("exception", "Not provided")}
            Exception type: {exception_result.get("exception_type", "Not provided")}
            Severity: {exception_result.get("severity", "Not provided")}

            Find the most relevant logistics operational procedures,
            escalation policies, customs procedures, carrier policies,
            and weather or port disruption guidance for this shipment.
            """.strip()
def retrieve_for_shipment(shipment, exception_result, k=None):
    query = build_shipment_query(
        shipment,
        exception_result
    )

    return retrieve(query, k=k)


if __name__ == "__main__":
    query = (
        "A critical shipment is delayed and requires "
        "immediate operational escalation."
    )

    results = retrieve(query)

    for number, result in enumerate(results, start=1):
        print(f"\n--- Result {number} ---")
        print(f"Source: {result['source']}")
        print(f"Distance: {result['distance']:.4f}")
        print(result["content"])