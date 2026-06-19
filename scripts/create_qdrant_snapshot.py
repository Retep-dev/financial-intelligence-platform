from db.qdrant.snapshots import create_snapshot


if __name__ == "__main__":
    snapshot = create_snapshot()
    print(f"Snapshot created: {snapshot}")
