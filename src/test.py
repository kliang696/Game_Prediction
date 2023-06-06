from google.cloud import storage
from pathlib import Path

def upload_to_cloud_storage(bucket_name: str, file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} does not exist")
    if not file_path.is_file():
        raise FileNotFoundError(f"{file_path} is not a file")
    
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    if not bucket.exists():
        bucket.create()
    
    blob = bucket.blob(file_path.name)
    blob.upload_from_filename(file_path)


if __name__ == "__main__":
    upload_to_cloud_storage("daily-game-stats", Path("out/game_info.csv"))
