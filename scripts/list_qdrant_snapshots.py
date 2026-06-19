from db.qdrant.snapshots import list_snapshots


if __name__ == "__main__":
    snapshots = list_snapshots()
    print(f"Found {len(snapshots)} snapshots:")
    for snapshot in snapshots:
        print(f"  - {snapshot.name} ({snapshot.size} bytes)")
