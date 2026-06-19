from typing import Optional

from db.qdrant.client import get_qdrant_client
from db.qdrant.collections import COLLECTION_NAME


def create_snapshot() -> dict:
    """Create a snapshot of the financial_chunks collection."""
    client = get_qdrant_client()
    return client.create_snapshot(collection_name=COLLECTION_NAME)


def list_snapshots() -> list:
    """List available snapshots for the collection."""
    client = get_qdrant_client()
    return client.list_snapshots(collection_name=COLLECTION_NAME)


def delete_snapshot(snapshot_name: str) -> bool:
    """Delete a snapshot by name."""
    client = get_qdrant_client()
    try:
        client.delete_snapshot(
            collection_name=COLLECTION_NAME,
            snapshot_name=snapshot_name
        )
        return True
    except Exception:
        return False


def recover_from_snapshot(snapshot_name: str) -> dict:
    """Recover the collection from a snapshot."""
    client = get_qdrant_client()
    return client.recover_snapshot(
        collection_name=COLLECTION_NAME,
        location=snapshot_name
    )
