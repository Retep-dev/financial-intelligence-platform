import json

from db.postgres.session import SessionLocal
from services.evaluation.models import EvaluationExample
from services.evaluation.runner import run_evaluation


# Example evaluation dataset
EVALUATION_DATASET = [
    EvaluationExample(
        query="How much did the cloud services segment grow?",
        expected_chunk_ids=["2d29611b-dbea-4e85-822d-4dd79290492c"]
    ),
    EvaluationExample(
        query="What was the revenue growth percentage?",
        expected_chunk_ids=["2d29611b-dbea-4e85-822d-4dd79290492c"]
    )
]


def main():
    db = SessionLocal()
    try:
        report = run_evaluation(
            db=db,
            examples=EVALUATION_DATASET,
            top_k=10,
            top_n=5,
            use_llm=False
        )

        print(json.dumps(report["metrics"], indent=2))

        with open("evaluation_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        print("\nDetailed report saved to evaluation_report.json")

    finally:
        db.close()


if __name__ == "__main__":
    main()
