from google.cloud import bigquery
import datetime
import pandas as pd

partition_date = datetime.datetime(2023, 6, 28) # You can change this for testing purposes
client = bigquery.Client()
dataset = client.dataset('daily_game_stats')
table = dataset.table(f'game_info_test${partition_date.strftime("%Y%m%d")}')

job_config = bigquery.LoadJobConfig()
job_config.autodetect = True
job_config.source_format = bigquery.SourceFormat.CSV
job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
job_config.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field='Date',
)

df = pd.DataFrame({'Date': [partition_date, partition_date], 'GameID': [1, 2]})

job = client.load_table_from_dataframe(df, table, job_config=job_config)

job.result()