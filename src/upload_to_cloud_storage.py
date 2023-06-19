from google.cloud import bigquery
# Instantiate a BigQuery client
bq_client = bigquery.Client()

source_uri = "gs://daily-game-stats/game_info.csv"
dataset_id = "my_dataset"
table_id = "my_table"

# Define the job configuration for the load job
job_config = bigquery.LoadJobConfig(
    autodetect=True,  # Auto-detect the schema
    source_format=bigquery.SourceFormat.CSV,  # Define source format
)

# Define the destination table reference
table_ref = bq_client.dataset(dataset_id).table(table_id)

# Start the load job
load_job = bq_client.load_table_from_uri(source_uri, table_ref, job_config=job_config)

# Wait for the job to complete
load_job.result()

print("Data loaded successfully.")
