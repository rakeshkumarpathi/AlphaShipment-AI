import json
from pathlib import Path

from src.rag.retriever import retrieve


DATASET_PATH = Path("evaluation/retrieval_dataset.json")

K = 4


def unique_sources(results):
    """
    Keep the first occurrence of each source while
    preserving retrieval order.
    """
    sources = []

    for result in results:
        source = result["source"]

        if source not in sources:
            sources.append(source)

    return sources


def precision_at_k(retrieved_sources, relevant_sources, k):
    retrieved = retrieved_sources[:k]

    if k == 0:
        return 0.0

    relevant_count = sum(
        source in relevant_sources
        for source in retrieved
    )

    return relevant_count / k


def recall_at_k(retrieved_sources, relevant_sources, k):
    retrieved = retrieved_sources[:k]

    if not relevant_sources:
        return 0.0

    retrieved_relevant = {
        source
        for source in retrieved
        if source in relevant_sources
    }

    return len(retrieved_relevant) / len(relevant_sources)

def main():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        dataset = json.load(file)

    evaluation_results = []

    precision_scores = []
    recall_scores = []

    for item in dataset:

        query = item["query"]
        relevant_sources = set(
            item["relevant_sources"]
        )

        results = retrieve(
            query,
            k=K
        )

        retrieved_sources = [
            result["source"]
            for result in results
        ]

        precision = precision_at_k(
            retrieved_sources,
            relevant_sources,
            K
        )

        recall = recall_at_k(
            retrieved_sources,
            relevant_sources,
            K
        )

        precision_scores.append(precision)
        recall_scores.append(recall)

        evaluation_results.append(
            {
                "query": query,
                "relevant_sources": sorted(
                    relevant_sources
                ),
                "retrieved_sources": retrieved_sources,
                "precision_at_k": precision,
                "recall_at_k": recall
            }
        )

        print("\n========================================")
        print("Query:")
        print(query)

        print("\nExpected:")
        for source in relevant_sources:
            print(f"  ✓ {source}")

        print("\nRetrieved:")
        for rank, source in enumerate(
            retrieved_sources[:K],
            start=1
        ):
            marker = (
                "✓"
                if source in relevant_sources
                else "✗"
            )

            print(
                f"  {rank}. {marker} {source}"
            )

        print(
            f"\nPrecision@{K}: "
            f"{precision:.2f}"
        )

        print(
            f"Recall@{K}: "
            f"{recall:.2f}"
        )

    mean_precision = (
        sum(precision_scores)
        / len(precision_scores)
    )

    mean_recall = (
        sum(recall_scores)
        / len(recall_scores)
    )

    summary = {
        "k": K,
        "number_of_queries": len(dataset),
        "mean_precision_at_k": mean_precision,
        "mean_recall_at_k": mean_recall,
        "results": evaluation_results
    }

    with open(
        "evaluation/results.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n========================================")
    print("RAG EVALUATION SUMMARY")
    print("========================================")

    print(
        f"Queries evaluated: "
        f"{len(dataset)}"
    )

    print(
        f"Mean Precision@{K}: "
        f"{mean_precision:.2%}"
    )

    print(
        f"Mean Recall@{K}: "
        f"{mean_recall:.2%}"
    )

    print(
        "\nResults saved to:"
        "\nevaluation/results.json"
    )


if __name__ == "__main__":
    main()