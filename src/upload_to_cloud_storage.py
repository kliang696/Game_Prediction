from google.cloud import bigquery
# Instantiate a BigQuery client
bq_client = bigquery.Client()

source_uri = "gs://daily-game-stats/game_info.csv"
dataset_id = "my_dataset"
table_id = "my_table5$20230607"

# Define the job configuration for the load job
job_config = bigquery.LoadJobConfig(
    autodetect=True,  # Auto-detect the schema
    source_format=bigquery.SourceFormat.CSV,  # Define source format
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
)

dataset_ref = bq_client.dataset(dataset_id)
# create the dataset if it doesn't exist
dataset = bigquery.Dataset(dataset_ref)
dataset = bq_client.create_dataset(dataset, exists_ok=True)

table_ref = dataset_ref.table(table_id)

# Start the load job
load_job = bq_client.load_table_from_uri(source_uri, table_ref, job_config=job_config)

# Wait for the job to complete
load_job.result()

print("Data loaded successfully.")
