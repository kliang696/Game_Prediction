from google.cloud import storage
storage_client = storage.Client()
bucket=storage_client.get_bucket("daily-game-stats")
blob = bucket.blob('my-blob')

with open('out/game_info.csv', 'rb') as my_file:
    blob.upload_from_file(my_file)